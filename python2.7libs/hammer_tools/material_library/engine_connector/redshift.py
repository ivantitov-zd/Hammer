import os

import hou

from .. import ui
from ..image import loadImage
from ..path import TEMP_IMAGE_PATH
from ..texture_format import TextureFormat
from .engine_connector import EngineConnector
from .builder import RedshiftNetworkBuilder
from ..thumbnail import MaterialPreviewScene


class RedshiftConnector(EngineConnector):
    def __init__(self):
        super(RedshiftConnector, self).__init__()

    def isAvailable(self):
        return hou.nodeType(hou.ropNodeTypeCategory(), 'Redshift_ROP') is not None

    def id(self):
        return 'redshift:1'

    def name(self):
        return 'Redshift'

    def icon(self):
        icon_name = hou.nodeType(hou.ropNodeTypeCategory(), 'Redshift_ROP').icon()
        return ui.icon(icon_name, 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        _, namespace, name, _ = node_type.nameComponents()

        if namespace.lower() == 'redshift':
            return True

        if isinstance(node_type, hou.VopNodeType) and 'redshift' in node_type.renderMask().lower():
            return True

        if name.lower().startswith('rs_'):
            return True

        if 'redshift' in name.lower():
            return True

        return False

    def builders(self):
        return RedshiftNetworkBuilder(self),

    def canCreateThumbnail(self):
        return True

    def createThumbnail(self, material, options=None):
        scene = MaterialPreviewScene()

        scene.render_node = scene.out_node.createNode('ifd')
        scene.render_node.parm('camera').set(scene.cam_node.path())
        scene.render_node.parm('vobject').set(scene.obj_node.path() + '/*')
        scene.render_node.parm('alights').set(scene.obj_node.path() + '/*')
        scene.render_node.parm('res_fraction').set('specific')
        scene.render_node.parmTuple('res_override').set((256, 256))

        builder = RedshiftNetworkBuilder(self)
        material_node = builder.build(material, '/mat/')
        scene.geo_node.parm('shop_materialpath').set(material_node.path())

        scene.render_node.parm('vm_picture').set(TEMP_IMAGE_PATH)
        scene.render_node.parm('execute').pressButton()

        image = loadImage(TEMP_IMAGE_PATH)
        os.remove(TEMP_IMAGE_PATH)
        scene.destroy()
        return image

    def supportedTextureFormats(self):
        return TextureFormat.wrap(r'rs\w+bin', 'exr', 'ptx', 'ptex', 'hdr', 'png', 'tga', 'tif', 'tiff', 'jpg', 'jpeg')


EngineConnector.registerEngine(RedshiftConnector)
