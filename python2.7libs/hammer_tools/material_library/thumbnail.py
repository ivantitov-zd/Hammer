import os
import tempfile

try:
    from PyQt5.QtGui import QImage
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtGui import QImage
    from PySide2.QtCore import Qt

import hou

from .db import connect
from .engine_connector.builder import MantraPrincipledBuilder
from .image import loadImage
from .operation import InterruptableOperation


class MaterialPreviewScene(object):
    def __init__(self, root='/out/'):
        self.out_node = hou.node('/out/')

        self.obj_node = hou.node(root).createNode('objnet')

        self.env_node = self.obj_node.createNode('envlight')
        self.env_node.parm('ry').set(190)
        self.env_node.parm('env_map').set('photo_studio_01_2k.hdr')

        self.cam_node = self.obj_node.createNode('cam')
        self.cam_node.parmTuple('t').set((-0.4, 0, 0.7))
        self.cam_node.parm('ry').set(-30)
        self.cam_node.parmTuple('res').set((256, 256))

        self.geo_node = self.obj_node.createNode('geo')

        self.sphere_node = self.geo_node.createNode('sphere')
        self.sphere_node.parm('type').set('polymesh')
        self.sphere_node.parm('scale').set(0.27)

        self.uv_node = self.geo_node.createNode('texture')
        self.uv_node.parm('type').set('polar')
        self.uv_node.parm('fixseams').set(True)
        self.uv_node.setRenderFlag(True)
        self.uv_node.setDisplayFlag(True)
        self.uv_node.setFirstInput(self.sphere_node)

    def destroy(self):
        with hou.undos.disabler():
            self.render_node.destroy()
            self.material_node.destroy()
            self.obj_node.destroy()


def generateMaterialThumbnails(materials, engine, options=None, external_connection=None):
    if not materials:
        return

    if external_connection is None:
        connection = connect()
        connection.execute('BEGIN')
    else:
        connection = external_connection

    material_count = len(materials)
    with InterruptableOperation(
            count=material_count,
            operation='Thumbnail rendering',
            icon='SOP_material',
            parent=hou.qt.mainWindow()
    ) as operation:
        with hou.undos.disabler():
            for index, material in enumerate(materials, 1):
                thumbnail = engine.createThumbnail(material, options)
                material.addThumbnail(thumbnail, engine.id(), external_connection=connection)
                try:
                    operation.updateProgress(index, 'Rendering  {} / {}'.format(index, material_count))
                except hou.OperationInterrupted:
                    break  # Todo: Flash message

    if external_connection is None:
        connection.commit()
        connection.close()


def generateTextureThumbnails(textures, external_connection=None):
    if not textures:
        return

    if external_connection is None:
        connection = connect()
        connection.execute('BEGIN')
    else:
        connection = external_connection

    with InterruptableOperation(
            count=len(textures),
            operation='Thumbnail creating',
            icon='BUTTONS_parmmenu_texture',
            parent=hou.qt.mainWindow()
    ) as operation:
        operation.updateProgress(status='Converting and scaling textures')
        for num, texture in enumerate(textures, 1):
            format_collision = set(texture.formats()).intersection(
                {'png', 'bmp', 'tga', 'tif', 'tiff', 'jpg', 'jpeg'}
            )
            if format_collision:
                image = QImage(texture.path(format_collision.pop()))
            else:
                image = loadImage(texture.path())
            texture.addThumbnail(image.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                 external_connection=connection)
            try:
                operation.updateProgress(num)
            except hou.OperationInterrupted:
                break  # Todo: Flash message

    if external_connection is None:
        connection.commit()
        connection.close()
