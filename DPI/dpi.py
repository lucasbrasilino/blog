from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

log = core.getLogger()


class DPI(object):
    def __init__ (self):
        core.openflow.addListeners(self)
        log.info("Registering DPI component")
        self.cam = dict()

    def isCommonSwitch(self, dpid):
        if dpid < 3:
            return True
        else:
            return False

    def _handle_ConnectionUp (self, event):
        log.info("Switch %d connecting" % event.dpid)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        log.info("Switch %d connecting" % event.dpid)
        if self.isCommonSwitch(event.dpid):
            self.cam[(event.dpid,packet.src)] = event.port
            if packet.dst.is_multicast:
                self.flood(event)
            elif (event.dpid,packet.dst) not in self.cam:
                self.flood(event)
            else:
                out_port = self.macToPort[(event.dpid,packet.dst)]
                log.info("Installing table entry: %s.%i -> %s.%i" %
                         (packet.src, event.port, packet.dst, out_port))
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match(dl_src = packet.src, 
                                         dl_dst = packet.dst,
                                         dl_type = packet.type)
                msg.data = event.ofp
                msg.actions.append(of.ofp_action_output(port = out_port))
                event.connection.send(msg)
