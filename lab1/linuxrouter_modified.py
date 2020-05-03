#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router
This example converts a Node into a router using IP forwarding
already built into Linux.
The example topology creates 2 routers and 4 IP subnets:
    - 10.0.0.0/24 (r0-eth1, IP: 10.0.0.1)
    - 10.0.2.0/24 (r0-eth2, IP: 10.0.2.1)
    - 10.0.1.0/24 (r1-eth1, IP: 10.0.1.1)
    - 10.0.3.0/24 (r1-eth2, IP: 10.0.3.1)
Each subnet consists of a single host connected to
a single switch:
    r0-eth1 - s1-eth1 - h1-eth0 (IP: 10.0.0.100)
    r1-eth1 - s3-eth1 - h1-eth0 (IP: 10.0.1.100)
    r0-eth2 - s2-eth1 - h2-eth0 (IP: 10.0.2.100)
    r1-eth2 - s4-eth1 - h2-eth0 (IP: 10.0.3.100)
The example relies on default routing entries that are
automatically created for each router interface, as well
as 'defaultRoute' parameters for the host interfaces.
Additional routes may be added to the router or hosts by
executing 'ip route' or 'route' commands on the router or hosts.
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting 4 IP subnets"

    def build( self, **_opts ):

        defaultIP = '10.0.0.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        defaultIP2 = '10.0.1.1/24'  # IP address for r1-eth1
        router2 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP2 )

        s1, s2, s3, s4= [ self.addSwitch( s ) for s in ( 's1', 's2', 's3', 's4' ) ]

        self.addLink( s1, router, intfName2='r0-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s3, router2, intfName2='r1-eth1',
                      params2={ 'ip' : '10.0.1.1/24' } )
        self.addLink( s2, router, intfName2='r0-eth2',
                      params2={ 'ip' : '10.0.2.1/24' } )
        self.addLink( s4, router2, intfName2='r1-eth2',
                      params2={ 'ip' : '10.0.3.1/24' } )

        h1 = self.addHost( 'h1', ip='10.0.0.100/24',
                           defaultRoute='via 10.0.0.1' )
        
        h2 = self.addHost( 'h2', ip='10.0.2.100/24',
                           defaultRoute='via 10.0.2.1' )
        

        for h, s in [ (h1, s1), (h2, s2), (h1, s3), (h2, s4) ]:
            self.addLink( h, s )


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net['r0'].setIP( ip='10.0.2.1/24',
                           intf='r0-eth2' )
    net['r1'].setIP( ip='10.0.3.1/24',
                           intf='r1-eth2' )

    net['h1'].setIP( ip='10.0.1.100/24',
                           intf='h1-eth1' )
    net['h2'].setIP( ip='10.0.3.100/24',
                           intf='h2-eth1' )

    net['h1'].cmd('ip rule add from 10.0.0.100 table 1')
    net['h1'].cmd('ip rule add from 10.0.1.100 table 2')

    # Configure the two different routing tables
    net['h1'].cmd('ip route add 10.0.0.0/24 dev h1-eth0 scope link table 1')
    net['h1'].cmd('ip route add default via 10.0.0.1 dev h1-eth0 table 1')

    net['h1'].cmd('ip route add 10.0.1.0/24 dev h1-eth1 scope link table 2')
    net['h1'].cmd('ip route add default via 10.0.1.1 dev h1-eth1 table 2')

    # default route for the selection process of normal internet-traffic
    net['h1'].cmd('ip route add default scope global nexthop via 10.0.0.1 dev h1-eth0')

    net['h2'].cmd('ip rule add from 10.0.2.100 table 1')
    net['h2'].cmd('ip rule add from 10.0.3.100 table 2')

    # Configure the two different routing tables
    net['h2'].cmd('ip route add 10.0.2.0/24 dev h2-eth0 scope link table 1')
    net['h2'].cmd('ip route add default via 10.0.2.1 dev h2-eth0 table 1')

    net['h2'].cmd('ip route add 10.0.3.0/24 dev h2-eth1 scope link table 2')
    net['h2'].cmd('ip route add default via 10.0.3.1 dev h2-eth1 table 2')

    # default route for the selection process of normal internet-traffic
    net['h2'].cmd('ip route add default scope global nexthop via 10.0.2.1 dev h2-eth0')




    net['h1'].cmd('ip route add 10.0.2.0/24 via 10.0.0.1 dev h1-eth0 table 1')
    net['h1'].cmd('ip route add 10.0.3.0/24 via 10.0.1.1 dev h1-eth1 table 2')
    net['h2'].cmd('ip route add 10.0.0.0/24 via 10.0.2.1 dev h2-eth0 table 1')
    net['h2'].cmd('ip route add 10.0.1.0/24 via 10.0.3.1 dev h2-eth1 table 2')



    
    net['h1'].cmd('tc qdisc add dev h1-eth0 root tbf rate 1mbit')
    net['h1'].cmd('tc qdisc add dev h1-eth1 root tbf rate 1mbit')
    net['h2'].cmd('tc qdisc add dev h2-eth0 root tbf rate 1mbit')
    net['h2'].cmd('tc qdisc add dev h2-eth1 root tbf rate 1mbit')
    net['r0'].cmd('tc qdisc add dev r0-eth1 root tbf rate 1mbit')
    net['r0'].cmd('tc qdisc add dev r0-eth2 root tbf rate 1mbit')
    net['r1'].cmd('tc qdisc add dev r1-eth1 root tbf rate 1mbit')
    net['r1'].cmd('tc qdisc add dev r1-eth2 root tbf rate 1mbit')


    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    info( net[ 'r1' ].cmd( 'route' ) )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()