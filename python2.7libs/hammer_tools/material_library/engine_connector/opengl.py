import hou

from .engine_connector import EngineConnector


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
        return hou.qt.Icon('ROP_opengl', 16, 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        return 'opengl' in node_type.name().lower()

    def supportedTextureFormats(self):
        return ('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'jpg', 'jpeg',
                'hdr', 'tif', 'tif3', 'tif16', 'tif32', 'tiff', 'pic')


EngineConnector.registerEngine(OpenGLConnector)
