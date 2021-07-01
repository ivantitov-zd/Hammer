import os

import hou

from .. import ui
from ..image import loadImage
from ..path import TEMP_IMAGE_PATH
from ..texture_format import TextureFormat
from ..thumbnail import MaterialPreviewScene
from .engine_connector import EngineConnector
from .builder import OpenGLPrincipledBuilder, MantraPrincipledBuilder


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
        return MantraPrincipledBuilder(self),

    def canCreateThumbnail(self):
        return True

    def createThumbnail(self, material, options):
        scene = MaterialPreviewScene()

        scene.render_node = scene.out_node.createNode('opengl')
        # Scene tab
        scene.render_node.parm('camera').set(scene.cam_node.path())
        scene.render_node.parm('scenepath').set(scene.obj_node.path())
        scene.render_node.parm('tres').set(True)
        scene.render_node.parmTuple('res').set((256, 256))
        # Output tab
        scene.render_node.parm('colorcorrect').set('lut_gamma')
        scene.render_node.parm('gamma').set(2.2)
        # Display Options tab
        scene.render_node.parm('aamode').set('aa8')
        scene.render_node.parm('usehdr').set('fp32')
        scene.render_node.parm('hqlighting').set(True)
        scene.render_node.parm('lightsamples').set(64)
        scene.render_node.parm('shadows').set(False)
        scene.render_node.parm('reflection').set(True)

        builder = MantraPrincipledBuilder(self)
        scene.material_node = builder.build(material, '/mat/')
        scene.geo_node.parm('shop_materialpath').set(scene.material_node.path())

        # Fix for metallic materials in 18.0
        major_version, minor_version, build_version = hou.applicationVersion()
        if major_version == 18 and minor_version == 0:  # Fixme
            scene.render_node.parm('hqlighting').set(scene.material_node.parm('metallic_useTexture').eval())
        elif major_version == 18 and minor_version == 5:
            scene.render_node.parm('reflection').set(
                scene.material_node.parm('metallic_useTexture').eval() or
                scene.material_node.parm('reflect_useTexture').eval()
            )

        scene.render_node.parm('picture').set(TEMP_IMAGE_PATH)
        scene.render_node.parm('execute').pressButton()

        image = loadImage(TEMP_IMAGE_PATH)
        os.remove(TEMP_IMAGE_PATH)
        scene.destroy()
        hou.hscript('glcache -c')
        return image

    def supportedTextureFormats(self):
        return TextureFormat.wrap('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'hdr', 'tif', 'tif3', 'tif16', 'tif32',
                                  'tiff', 'pic', 'jpg', 'jpeg')


EngineConnector.registerEngine(OpenGLConnector)
