from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h1 = self.addHost( 'h1', ip='10.0.0.1/16', defaultRoute='via 10.0.0.1' )
        h2 = self.addHost( 'h2', ip='10.0.0.2/16', defaultRoute='via 10.0.0.1' )
        h3 = self.addHost( 'h3', ip='10.0.0.3/16', defaultRoute='via 10.0.0.1' )
        h4 = self.addHost( 'h4', ip='10.0.1.2/16', defaultRoute='via 10.0.1.1' )
        h5 = self.addHost( 'h5', ip='10.0.1.3/16', defaultRoute='via 10.0.1.1' )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )

        for h, s in [ (h1, s1), (h2, s1), (h3, s1), (h4, s3), (h5, s3), (s1, s2), (s2, s3) ]:
            self.addLink( h, s )


topos = { 'mytopo': ( lambda: MyTopo() ) }