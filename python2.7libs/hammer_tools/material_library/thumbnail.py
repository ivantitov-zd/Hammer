import os
import tempfile

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PySide2.QtGui import QImage

import hou

from .db.connect import connect
from .engine_connector.builder import MantraPrincipledBuilder


class MaterialPreviewScene(object):
    def __init__(self, engine=None):
        self.engine = engine

        with hou.undos.disabler():
            self.obj_node = hou.node('/obj/')

            self.env_node = self.obj_node.createNode('envlight')
            self.env_node.parm('envmap').set('photo_studio_01_2k.rat')

            self.cam_node = self.obj_node.createNode('cam')
            self.cam_node.parmTuple('t').set((-0.4, 0, 0.7))
            self.cam_node.parm('ry').set(-30)
            self.cam_node.parmTuple('res').set((256, 256))

            self.geo_node = self.obj_node.createNode('geo')

            self.sphere_node = self.geo_node.createNode('sphere')
            self.sphere_node.parm('type').set(5)  # Bezier prim type used for UV
            self.sphere_node.parm('scale').set(0.27)

            self.out_node = hou.node('/out/')

            if self.engine is None:
                self.render_node = self.out_node.createNode('opengl')
                # Scene tab
                self.render_node.parm('camera').set(self.cam_node.path())
                self.render_node.parm('tres').set(True)
                self.render_node.parmTuple('res').set((256, 256))
                # Output tab
                self.render_node.parm('colorcorrect').set('lut_gamma')
                self.render_node.parm('gamma').set(2.2)
                # Display Options tab
                self.render_node.parm('aamode').set('aa8')
                self.render_node.parm('usehdr').set('fp32')
                self.render_node.parm('hqlighting').set(True)
                self.render_node.parm('lightsamples').set(64)
                self.render_node.parm('shadows').set(False)
                self.render_node.parm('reflection').set(True)
            else:
                self.render_node = self.engine.createThumbnailRenderNode(self)

    def setEnvironmentMap(self):
        pass

    def setGeometry(self):
        pass

    def render(self, material):
        with hou.undos.disabler():
            path = os.path.join(tempfile.gettempdir(), str(os.getpid()) + 'hammer_mat_lib_thumb.png').replace('\\', '/')

            if self.engine is None:
                material_node = MantraPrincipledBuilder().build(material, '/mat/')
                self.geo_node.parm('shop_materialpath').set(material_node.path())
                self.render_node.parm('picture').set(path)
                self.render_node.parm('hqlighting').set(material_node.parm('metallic_useTexture').eval())
            else:
                material_node = self.engine.builders()[0]().build(material, '/mat/')
            self.render_node.parm('execute').pressButton()
            image = QImage(path)
            material_node.destroy()
            os.unlink(path)
        return image

    def destroy(self):
        try:
            with hou.undos.disabler():
                self.render_node.destroy()
                self.env_node.destroy()
                self.cam_node.destroy()
                self.geo_node.destroy()
        except hou.ObjectWasDeleted:
            return


def updateMaterialThumbnails(materials, engine=None, external_connection=None):
    scene = MaterialPreviewScene(engine)
    if external_connection is None:
        connection = connect()
        connection.execute('BEGIN')
    else:
        connection = external_connection

    for material in materials:
        material.addThumbnail(scene.render(material), None, connection)
        hou.hscript('glcache -c')
    scene.destroy()

    if external_connection is None:
        connection.commit()
        connection.close()
