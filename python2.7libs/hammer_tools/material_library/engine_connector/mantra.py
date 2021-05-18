import hou

from .engine_connector import EngineConnector
from .builder import MantraPrincipledBuilder, MantraPrincipledNetworkBuilder


class MantraConnector(EngineConnector):
    def __init__(self):
        super(MantraConnector, self).__init__()

    def isAvailable(self):
        return True

    def name(self):
        return 'Mantra'

    def icon(self):
        return hou.qt.Icon('ROP_mantra', 16, 16)

    def id(self):
        return 'mantra::1'

    def builders(self):
        return MantraPrincipledBuilder, MantraPrincipledNetworkBuilder

    def supportedTextureFormats(self):
        return ('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'jpg', 'jpeg',
                'hdr', 'tif', 'tif3', 'tif16', 'tif32', 'tiff', 'pic')


EngineConnector.registerEngine(MantraConnector)
