#!/usr/bin/python

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        h5 = self.addHost( 'h5' )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )

        for h, s in [ (h1, s1), (h2, s1), (h3, s1), (h4, s3), (h5, s3), (s1, s2), (s2, s3) ]:
            self.addLink( h, s )


opos = { 'mytopo': ( lambda: MyTopo() ) }
