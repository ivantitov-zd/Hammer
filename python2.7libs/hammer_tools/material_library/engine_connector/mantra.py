import hou

from ..texture_map.texture_format import TextureFormat
from .engine_connector import EngineConnector
from .builder import MantraPrincipledBuilder


class MantraConnector(EngineConnector):
    def __init__(self):
        super(MantraConnector, self).__init__()

    def isAvailable(self):
        return True

    def id(self):
        return 'mantra::1'

    def name(self):
        return 'Mantra'

    def icon(self):
        return hou.qt.Icon('ROP_mantra', 16, 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        if 'mantra' in node_type.description().lower():
            return True

        _, _, name, _ = node_type.nameComponents()

        if name.lower() == 'ifd':
            return True

        if isinstance(node_type, hou.VopNodeType) and 'mantra' in node_type.renderMask().lower():
            return True

        return False

    def builders(self):
        return MantraPrincipledBuilder(self),

    def supportedTextureFormats(self):
        return TextureFormat.wrap('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'hdr', 'tif', 'tif3', 'tif16', 'tif32',
                                  'tiff', 'pic', 'jpg', 'jpeg')


EngineConnector.registerEngine(MantraConnector)
