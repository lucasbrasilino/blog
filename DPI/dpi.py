from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

log = core.getLogger()

IDLE_TIMEOUT = 10
HARD_TIMEOUT = 15

DPI_SWITCH = 3

class DPI(object):
    def __init__ (self, port):
        core.openflow.addListeners(self)
        log.info("Registering DPI component")
        self.diverted_port = int(port)
        self.cam = dict()
        self.flowMod = {
            1: self.flowModCommonSwitch,
            2: self.flowModCommonSwitch,
            3: self.flowModDPISwitch }

    def isCommonSwitch(self, dpid):
        if dpid < DPI_SWITCH:
            return True
        else:
            return False

    def _handle_ConnectionUp (self, event):
        log.info("Switch %d connecting" % event.dpid)

    def _handle_PacketIn (self, event):
        self.flowMod[event.dpid](event)

    def flood (self,event):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.in_port = event.port
        action = of.ofp_action_output(port = of.OFPP_FLOOD)
        msg.actions.append(action)
        event.connection.send(msg)

    def flowModCommonSwitch(self, event):
        packet = event.parsed
        self.cam[(event.dpid,packet.src)] = event.port
        if packet.dst.is_multicast:
            self.flood(event)
        elif (event.dpid,packet.dst) not in self.cam:
            self.flood(event)
        else:
            out_port = self.cam[(event.dpid,packet.dst)]
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet,event.port)
            msg.data = event.ofp
            msg.idle_timeout = IDLE_TIMEOUT
            msg.hard_timeout = HARD_TIMEOUT
            msg.actions.append(of.ofp_action_output(port = out_port))
            event.connection.send(msg)


    def flowModDPISwitch(self, event):
        log.info("Called flowModDPISwitch: %d" % event.dpid)
