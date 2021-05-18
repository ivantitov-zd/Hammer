import os
import tempfile

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PySide2.QtGui import QImage

import hou

from .db.connect import connect
from .material import Material
from .engine_connector.builder import MantraPrincipledBuilder

TEMP_THUMB_PATH = r'D:\opengl_thumbnails'


class ShadingScene(object):
    def __init__(self):
        with hou.undos.disabler():
            self.obj_node = hou.node('/obj/')

            self.cam_node = self.obj_node.createNode('cam')
            self.cam_node.parmTuple('t').set((-0.4, 0, 0.7))
            self.cam_node.parm('ry').set(-30)
            self.cam_node.parmTuple('res').set((256, 256))

            self.geo_node = self.obj_node.createNode('geo')

            self.sphere_node = self.geo_node.createNode('sphere')
            self.sphere_node.parm('type').set(5)  # Bezier prim type used for UV
            self.sphere_node.parm('scale').set(0.27)

            self.output_node = self.sphere_node.createOutputNode('output')

            self.out_node = hou.node('/out/')

            self.opengl_node = self.out_node.createNode('opengl')
            # Scene tab
            self.opengl_node.parm('camera').set(self.cam_node.path())
            self.opengl_node.parm('tres').set(True)
            self.opengl_node.parmTuple('res').set((256, 256))
            # Output tab
            self.opengl_node.parm('colorcorrect').set('lut_gamma')
            self.opengl_node.parm('gamma').set(2.2)
            # Display Options tab
            self.opengl_node.parm('aamode').set('aa8')
            self.opengl_node.parm('usehdr').set('fp32')
            self.opengl_node.parm('hqlighting').set(True)
            self.opengl_node.parm('lightsamples').set(64)
            self.opengl_node.parm('shadows').set(False)
            self.opengl_node.parm('reflection').set(True)

    def render(self, material):
        with hou.undos.disabler():
            node = MantraPrincipledBuilder().build(material, '/mat/')
            self.geo_node.parm('shop_materialpath').set(node.path())
            path = os.path.join(tempfile.gettempdir(), str(os.getpid()) + 'hammer_mat_lib_thumb.png').replace('\\', '/')
            self.opengl_node.parm('picture').set(path)
            self.opengl_node.parm('hqlighting').set(node.parm('metallic_useTexture').eval())
            self.opengl_node.parm('execute').pressButton()
            image = QImage(path)
            node.destroy()
            os.unlink(path)
        return image

    def destroy(self):
        try:
            with hou.undos.disabler():
                self.opengl_node.destroy()
                self.cam_node.destroy()
                self.geo_node.destroy()
        except hou.ObjectWasDeleted:
            return


def updateMaterialThumbnails():
    scene = ShadingScene()
    materials = Material.allMaterials()
    connection = connect()
    connection.execute('BEGIN')
    for index, material in enumerate(materials):
        material.addThumbnail(scene.render(material), None, connection)
        if index % 20 == 0:
            hou.hscript('glcache -c')
        print(int((index + 1) / float(len(materials)) * 100))
    scene.destroy()
    hou.hscript('glcache -c')
    connection.commit()
    connection.close()
