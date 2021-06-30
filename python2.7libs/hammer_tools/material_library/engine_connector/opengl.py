from .. import ui
from ..texture_format import TextureFormat
from .engine_connector import EngineConnector
from .builder.opengl_principled import OpenGLPrincipledBuilder


class OpenGLConnector(EngineConnector):
    def __init__(self):
        super(OpenGLConnector, self).__init__()

    def isAvailable(self):
        return True

    def id(self):
        return 'opengl::1'

    def name(self):
        return 'OpenGL'

    def icon(self):
        return ui.icon('ROP_opengl', 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        return 'opengl' in node_type.name().lower()

    def builders(self):
        return OpenGLPrincipledBuilder(self),

    def canCreateThumbnail(self):
        return True

    def createThumbnail(self, material, options):
        pass

    def supportedTextureFormats(self):
        return TextureFormat.wrap('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'hdr', 'tif', 'tif3', 'tif16', 'tif32',
                                  'tiff', 'pic', 'jpg', 'jpeg')


EngineConnector.registerEngine(OpenGLConnector)
