import os

import hou

from .. import ui
from ..image import loadImage
from ..path import TEMP_IMAGE_PATH
from ..texture_format import TextureFormat
from .engine_connector import EngineConnector
from .builder import MantraPrincipledBuilder
from ..thumbnail import MaterialPreviewScene


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
        return ui.icon('ROP_mantra', 16)

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

    def canCreateThumbnail(self):
        return True

    def createThumbnail(self, material, options=None):
        scene = MaterialPreviewScene()

        scene.render_node = scene.out_node.createNode('ifd')
        scene.render_node.parm('camera').set(scene.cam_node.path())
        scene.render_node.parm('vobject').set(scene.obj_node.path() + '/*')
        scene.render_node.parm('alights').set(scene.obj_node.path() + '/*')
        scene.render_node.parm('soho_autoheadlight').set(False)
        scene.render_node.parm('override_camerares').set(True)
        scene.render_node.parm('res_fraction').set('specific')
        scene.render_node.parmTuple('res_override').set((256, 256))
        scene.render_node.parm('vm_renderengine').set('pbrraytrace')
        scene.render_node.parmTuple('vm_samples').set((8, 8))
        scene.render_node.parm('vm_minraysamples').set(1)
        scene.render_node.parm('vm_maxraysamples').set(9)
        scene.render_node.parm('vm_dorayvariance').set(False)
        scene.render_node.parm('vm_variance').set(0.005)
        scene.render_node.parm('vm_transparentsamples').set(30)
        scene.render_node.parm('vm_reflectlimit').set(4)
        scene.render_node.parm('vm_refractlimit').set(4)
        scene.render_node.parm('vm_diffuselimit').set(3)
        scene.render_node.parm('vm_ssslimit').set(2)
        scene.render_node.parm('vm_volumelimit').set(3)
        scene.render_node.parm('vm_pbrpathtype').set('all')
        scene.render_node.parm('vm_usemaxthreads').set(2)  # All threads except one
        scene.render_node.parm('vm_writecheckpoint').set(False)
        scene.render_node.parm('soho_foreground').set(True)

        builder = MantraPrincipledBuilder(self)
        scene.material_node = builder.build(material, '/mat/')
        scene.geo_node.parm('shop_materialpath').set(scene.material_node.path())

        scene.render_node.parm('vm_picture').set(TEMP_IMAGE_PATH)
        scene.render_node.parm('execute').pressButton()

        image = loadImage(TEMP_IMAGE_PATH)
        os.remove(TEMP_IMAGE_PATH)
        scene.destroy()
        return image

    def supportedTextureFormats(self):
        return TextureFormat.wrap('rat', 'exr', 'ptx', 'ptex', 'png', 'tga', 'hdr', 'tif', 'tiff', 'tif3', 'tif16',
                                  'tif32', 'pic', 'jpg', 'jpeg')


EngineConnector.registerEngine(MantraConnector)
