#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController,OVSSwitch

class DPITopo(Topo):
	def __init__(self,**opts):
		Topo.__init__(self, **opts)
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')
		h1 = self.addHost('h1',mac="00:00:00:00:00:01",ip="10.0.0.1")
		h2 = self.addHost('h2',mac="00:00:00:00:00:02",ip="10.0.0.2")
		h3 = self.addHost('h3',mac="00:00:00:00:00:03",ip="10.0.0.3")
		self.addLink(s1,s2)
		self.addLink(s1,s3)
		self.addLink(s2,s3)
		self.addLink(h1,s1)
		self.addLink(h2,s1)
		self.addLink(h3,s2)

		
def runCmd(net):
	h1 = net.get('h1')
	h2 = net.get('h2')
	h3 = net.get('h3')
	print h1.cmd('ping -c1 10.0.0.2')

def topo():
	topo = DPITopo()
	net = Mininet(topo, switch=OVSSwitch, controller=None)
	net.addController( 'c0', controller=RemoteController, ip='192.168.56.1', port=6633 )
	net.start()
	runCmd(net)
	CLI(net)
	net.stop()

if __name__ == "__main__":
	setLogLevel('info')
	topo()	
