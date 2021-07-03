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

        displace_enable_parm = scene.geo_node.parm('RS_objprop_displace_enable')
        if displace_enable_parm is not None:
            displace_enable_parm.set(True)
            scene.geo_node.parm('RS_objprop_displace_scale').set(0.02)
            scene.geo_node.parm('RS_objprop_rstess_enable').set(True)

        scene.env_node = scene.env_node.changeNodeType('rslightdome', keep_parms=False, keep_network_contents=False)
        scene.env_node.parm('background_enable').set(False)
        abs_hdr_path = hou.findFile('pic/photo_studio_01_2k.hdr')
        try:
            scene.env_node.parm('env_map').set(abs_hdr_path)
        except AttributeError:
            pass
        try:
            scene.env_node.parm('tex0').set(abs_hdr_path)
        except AttributeError:
            pass

        scene.render_node = scene.out_node.createNode('Redshift_ROP')
        scene.render_node.parm('RS_renderCamera').set(scene.cam_node.path())
        scene.render_node.parm('RS_overrideCameraRes').set(True)
        scene.render_node.parm('RS_overrideResScale').set('user')
        scene.render_node.parmTuple('RS_overrideRes').set((256, 256))
        scene.render_node.parm('RS_nonBlockingRendering').set(False)
        scene.render_node.parm('RS_addDefaultLight').set(False)
        scene.render_node.parm('RS_renderToMPlay').set(False)
        scene.render_node.parm('RS_outputFileFormat').set('.png')
        scene.render_node.parm('RS_outputBitsPNG').set('INTEGER16')
        scene.render_node.parm('RS_aovAllAOVsDisabled').set(True)
        scene.render_node.parm('MaxTraceDepthReflection').set(4)
        scene.render_node.parm('MaxTraceDepthRefraction').set(4)
        scene.render_node.parm('CopyToTextureCache').set(False)
        # Todo: Turn on "Enable Refraction affects dome lights"
        scene.render_node.parm('PrimaryGIEngine').set('RS_GIENGINE_BRUTE_FORCE')
        # Todo: Use Photon map as secondary?
        scene.render_node.parm('SecondaryGIEngine').set('RS_GIENGINE_BRUTE_FORCE')
        scene.render_node.parm('NumGIBounces').set(3)
        # Todo: RTX and others new features

        builder = RedshiftNetworkBuilder(self)
        scene.material_node = builder.build(material, '/mat/')
        scene.geo_node.parm('shop_materialpath').set(scene.material_node.path())

        scene.render_node.parm('RS_outputFileNamePrefix').set(TEMP_IMAGE_PATH)
        scene.render_node.parm('execute').pressButton()

        image = loadImage(TEMP_IMAGE_PATH)
        os.remove(TEMP_IMAGE_PATH)
        scene.destroy()
        return image

    def supportedTextureFormats(self):
        return TextureFormat.wrap(r'rs\w+bin', 'hdr', 'exr', 'ptx', 'ptex', 'tga', 'tif', 'tiff', 'png', 'jpg', 'jpeg')


EngineConnector.registerEngine(RedshiftConnector)
