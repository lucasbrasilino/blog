from pox.core import core
from dpi import DPI

def launch(port = "80"):
    core.registerNew(DPI, port)
