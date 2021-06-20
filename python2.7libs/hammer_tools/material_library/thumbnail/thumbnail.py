import os
import subprocess
import tempfile

try:
    from PyQt5.QtGui import QImage
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtGui import QImage
    from PySide2.QtCore import Qt

import hou

from ..db import connect
from ..engine_connector.builder import MantraPrincipledBuilder
from ..image import loadImage


class MaterialPreviewScene(object):
    def __init__(self, engine=None):
        self.engine = engine

        with hou.undos.disabler():
            self.out_node = hou.node('/out/')

            self.obj_node = self.out_node.createNode('objnet')

            self.env_node = self.obj_node.createNode('envlight')
            self.env_node.parm('ry').set(190)
            self.env_node.parm('env_map').set('photo_studio_01_2k.rat')

            self.cam_node = self.obj_node.createNode('cam')
            self.cam_node.parmTuple('t').set((-0.4, 0, 0.7))
            self.cam_node.parm('ry').set(-30)
            self.cam_node.parmTuple('res').set((256, 256))

            self.geo_node = self.obj_node.createNode('geo')

            self.sphere_node = self.geo_node.createNode('sphere')
            self.sphere_node.parm('type').set(5)  # Bezier prim type used for UV
            self.sphere_node.parm('scale').set(0.27)

            if self.engine is None:
                self.render_node = self.out_node.createNode('opengl')
                # Scene tab
                self.render_node.parm('camera').set(self.cam_node.path())
                self.render_node.parm('scenepath').set(self.obj_node.path())
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
                pass
                # self.render_node = self.engine.createThumbnailRenderNode(self)

    def setEnvironmentMap(self, path):
        self.env_node.parm('env_map').set(path)

    def render(self, material):
        with hou.undos.disabler():
            image_path = os.path.join(tempfile.gettempdir(), str(os.getpid()) + 'hammer_mat_lib_thumb.png')
            image_path = image_path.replace('\\', '/')

            if self.engine is None:
                material_node = MantraPrincipledBuilder().build(material, '/mat/')
                self.geo_node.parm('shop_materialpath').set(material_node.path())
                self.render_node.parm('picture').set(image_path)

                # Fix for metallic materials in 18.0
                major_version, minor_version, build_version = hou.applicationVersion()
                if major_version == 18 and minor_version == 0:
                    self.render_node.parm('hqlighting').set(material_node.parm('metallic_useTexture').eval())
                else:
                    self.render_node.parm('hqlighting').set(True)
            else:
                material_node = self.engine.builders()[0]().build(material, '/mat/')

            self.render_node.parm('execute').pressButton()
            material_node.destroy()

        if self.engine is None:
            hou.hscript('glcache -c')

        image = QImage(image_path)
        os.remove(image_path)
        return image

    def destroy(self):
        try:
            with hou.undos.disabler():
                self.render_node.destroy()
                self.obj_node.destroy()
        except hou.ObjectWasDeleted:
            return


def updateMaterialThumbnails(materials, engine=None, hdri_path=None, external_connection=None):
    scene = MaterialPreviewScene(engine)
    if hdri_path:
        scene.setEnvironmentMap(hdri_path)

    if external_connection is None:
        connection = connect()
        connection.execute('BEGIN')
    else:
        connection = external_connection

    with hou.InterruptableOperation('Thumbnail rendering', open_interrupt_dialog=False) as op:
        try:
            material_count = float(len(materials))
        except TypeError:
            material_count = 1.0
        op.updateLongProgress(0)
        for num, material in enumerate(materials, 1):
            material.addThumbnail(scene.render(material), engine.id() if engine else None,
                                  external_connection=connection)
            try:
                op.updateLongProgress(num / material_count, 'Thumbnail {} / {}'.format(num, material_count))
            except hou.OperationInterrupted:
                break  # Todo: Flash message

    scene.destroy()

    if external_connection is None:
        connection.commit()
        connection.close()


def updateTextureThumbnails(textures, external_connection=None):
    if external_connection is None:
        connection = connect()
        connection.execute('BEGIN')
    else:
        connection = external_connection

    with hou.InterruptableOperation('Thumbnail rendering', open_interrupt_dialog=False) as op:
        try:
            texture_count = float(len(textures))
        except TypeError:
            texture_count = 1.0
        op.updateLongProgress(0)
        for num, texture in enumerate(textures, 1):
            format_collision = set(texture.formats()).intersection({'png', 'bmp', 'tga', 'tif', 'tiff', 'jpg', 'jpeg'})
            if format_collision:
                image = QImage(texture.path(format_collision.pop()))
            else:
                image = loadImage(texture.path())
            texture.addThumbnail(image.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                 external_connection=connection)
            try:
                op.updateLongProgress(num / texture_count, 'Thumbnail {} / {}'.format(num, texture_count))
            except hou.OperationInterrupted:
                break  # Todo: Flash message

    if external_connection is None:
        connection.commit()
        connection.close()
