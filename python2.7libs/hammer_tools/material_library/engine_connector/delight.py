import os
import time

import hou

from .. import ui
from ..image import loadImage
from ..path import TEMP_IMAGE_PATH
from ..texture_format import TextureFormat
from ..thumbnail import MaterialPreviewScene
from .engine_connector import EngineConnector
from .builder import DelightPrincipledBuilder


class DelightConnector(EngineConnector):
    def isAvailable(self):
        return hou.nodeType(hou.ropNodeTypeCategory(), '3Delight') is not None

    def id(self):
        return '3delight::1'

    def name(self):
        return '3Delight (Beta)'

    def icon(self):
        return ui.icon('ROP_3Delight', 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        _, namespace, name, _ = node_type.nameComponents()

        if namespace == '3Delight':
            return True

        if name == '3Delight':
            return True

        return False

    def builders(self):
        return DelightPrincipledBuilder(self),

    def canCreateThumbnail(self):
        return True

    def createThumbnail(self, material, options=None):
        scene = MaterialPreviewScene(None)

        scene.render_node = scene.out_node.createNode('3Delight')
        scene.render_node.parmTuple('f').deleteAllKeyframes()
        scene.render_node.parmTuple('f').set((1, 1, 1))
        scene.render_node.parm('camera').set(scene.cam_node.path())
        scene.render_node.parm('display_rendered_images').set(False)
        scene.render_node.parm('save_rendered_images').set(True)

        scene.render_node.parm('motion_blur').set(False)
        scene.render_node.parm('max_diffuse_depth').set(3)
        scene.render_node.parm('max_reflection_depth').set(4)
        scene.render_node.parm('max_refraction_depth').set(4)

        scene.render_node.parm('override_display_flags').set(True)
        scene.render_node.parm('objects_to_render').set(scene.geo_node.path())
        scene.render_node.parm('lights_to_render').set(scene.env_node.path())

        builder = DelightPrincipledBuilder(self)
        scene.material_node = builder.build(material, '/mat/')
        scene.geo_node.parm('shop_materialpath').set(scene.material_node.path())

        scene.render_node.parm('default_image_filename').set(TEMP_IMAGE_PATH)
        scene.render_node.parm('default_image_format').set('png')
        # scene.render_node.parm('default_image_bits').set('uint8')
        scene.render_node.parm('execute').pressButton()

        output_path = TEMP_IMAGE_PATH.replace('.png', '_rgba.png')
        image = None
        start_time = time.time()
        while image is None and time.time() - start_time < 30:
            time.sleep(4.5)
            image = loadImage(output_path)
        os.remove(output_path)
        scene.destroy()
        return image

    def supportedTextureFormats(self):
        return TextureFormat.wrap('tdl', 'hdr', 'exr', 'tga', 'tif', 'tiff', 'png', 'psd', 'pic',
                                  'jpg', 'jpeg', 'sgi', 'iff')


EngineConnector.registerEngine(DelightConnector)
