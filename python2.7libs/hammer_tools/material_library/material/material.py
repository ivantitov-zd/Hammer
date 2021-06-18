import os
import sqlite3

try:
    from PyQt5.QtCore import QBuffer, QIODevice
    from PyQt5.QtGui import QImage, QPixmap, QIcon
except ImportError:
    from PySide2.QtCore import QBuffer, QIODevice
    from PySide2.QtGui import QImage, QPixmap, QIcon

import hou

from ..db import connect
from ..texture import MapType, TextureMap
from ..image import imageToBytes
from .material_source import MaterialSource

MISSING_MATERIAL_THUMBNAIL_ICON = hou.qt.Icon('SOP_material', 256, 256)


class ThumbnailState:
    NotLoaded = 0
    Loaded = 1
    NotExists = 2


class Material(object):
    __slots__ = ('_id', '_name', '_comment', '_favorite', '_options', '_source_path', '_thumbnail_state', '_thumbnail',
                 '_thumbnail_engine_id', '_thumbnail_for_engine')

    @staticmethod
    def fromData(data):
        mat = Material()
        mat._id = data.get('id')
        mat._name = data['name']
        mat._comment = data.get('comment')
        mat._favorite = data.get('favorite', False)
        mat._options = data.get('options')
        mat._source_path = data['source_path'].replace('\\', '/')
        return mat

    def asData(self):
        return {
            'id': self.id(),
            'name': self.name(),
            'comment': self.comment(),
            'favorite': self.isFavorite(),
            'options': self._options,
            'source_path': self._source_path,
            'thumbnail': sqlite3.Binary(imageToBytes(self._thumbnail))
            if self._thumbnail and self._thumbnail != MISSING_MATERIAL_THUMBNAIL_ICON else None
        }

    @staticmethod
    def allMaterials():
        connection = connect()
        materials_data = connection.execute('SELECT id, name, comment, favorite, source_path FROM material').fetchall()
        connection.close()
        return tuple(Material.fromData(data) for data in materials_data)

    @staticmethod
    def addMaterial(material, external_connection=None):
        if isinstance(material, dict):
            material = Material.fromData(material)

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        cursor = connection.execute('INSERT INTO material (name, comment, favorite, options, source_path, thumbnail) '
                                    'VALUES (:name, :comment, :favorite, :options, :source_path, :thumbnail)',
                                    material.asData())
        material._id = cursor.lastrowid

        if external_connection is None:
            connection.commit()
            connection.close()
        return material

    @staticmethod
    def addMaterialsFromFolder(path, naming_mode=None, library=None, favorite=False, options=None):
        materials = []
        for root, _, files in os.walk(path):
            for file in files:
                if TextureMap.mapType(file) not in {MapType.Unknown, MapType.Thumbnail}:
                    mat = Material.fromData({
                        'name': os.path.basename(root),
                        'favorite': favorite,
                        'options': options,
                        'source_path': root
                    })
                    materials.append(mat)
                    break

        connection = connect()
        connection.execute('BEGIN')

        if library is not None:
            for mat in materials:
                try:
                    library.addMaterial(mat, external_connection=connection)
                except sqlite3.IntegrityError:
                    continue
        else:
            for mat in materials:
                try:
                    Material.addMaterial(mat, external_connection=connection)
                except sqlite3.IntegrityError:
                    continue

        connection.commit()
        connection.close()
        return tuple(mat for mat in materials if mat.id() is not None)

    def __init__(self):
        self._id = None
        self._name = None
        self._comment = None
        self._favorite = None
        self._options = None
        self._source_path = None
        self._thumbnail_state = ThumbnailState.NotLoaded
        self._thumbnail = None
        self._thumbnail_engine_id = None
        self._thumbnail_for_engine = None

    def id(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, Material):
            if self.id() and other.id():
                return self.id() == other.id()
            else:
                pass  # Todo: Compare attributes
        else:
            return NotImplemented

    def name(self):
        return self._name

    def comment(self):
        return self._comment

    def isFavorite(self):
        return self._favorite

    def markAsFavorite(self, state=True, external_connection=None):
        if self.id() is None:
            self._favorite = state
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('UPDATE material SET favorite = :state WHERE id = :material_id',
                           {'state': state, 'material_id': self.id()})

        self._favorite = state

        if external_connection is None:
            connection.commit()
            connection.close()

    def _loadDefaultThumbnail(self):
        if self.id() is None:
            return

        connection = connect()
        data = connection.execute('SELECT thumbnail AS image FROM material '
                                  'WHERE id = :material_id',
                                  {'material_id': self.id()}).fetchone()
        connection.close()
        if data['image']:
            self._thumbnail = QIcon(QPixmap.fromImage(QImage.fromData(bytes(data['image']), 'png')))
            self._thumbnail_state = ThumbnailState.Loaded
        else:
            self._thumbnail = None
            self._thumbnail_state = ThumbnailState.NotExists

    def thumbnail(self, engine=None, reload=False):
        if engine is not None and self.id():
            if engine.id() != self._thumbnail_engine_id:
                connection = connect()
                data = connection.execute('SELECT image FROM material_thumbnail '
                                          'WHERE material_id = :material_id AND engine_id = :engine_id',
                                          {'material_id': self.id(), 'engine_id': engine.id()}).fetchone()
                connection.close()
                if data is not None:
                    self._thumbnail_for_engine = QIcon(
                        QPixmap.fromImage(QImage.fromData(bytes(data['image']), 'png'))
                    )
                    self._thumbnail_engine_id = engine.id()
                    return self._thumbnail_for_engine
            else:
                return self._thumbnail_for_engine

        if not self._thumbnail and self._thumbnail_state == ThumbnailState.NotLoaded or reload:
            self._loadDefaultThumbnail()
        return self._thumbnail

    def addThumbnail(self, image, engine_id=None, external_connection=None):
        if self.id() is None:
            self._thumbnail = image
            return

        image_data = sqlite3.Binary(imageToBytes(image))

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if engine_id is None:
            connection.execute('UPDATE material SET thumbnail = :image WHERE id = :id',
                               {'id': self.id(), 'image': image_data})
        else:
            connection.execute('INSERT OR UPDATE INTO material VALUES (:material_id, :engine_id, :image)',
                               {'material_id': self.id(), 'engine_id': engine_id, 'image': image_data})

        if external_connection is None:
            connection.commit()
            connection.close()

    def options(self):
        return self._options

    def source(self):
        return MaterialSource(self, self._source_path)

    def path(self):
        return self._source_path

    def textureMaps(self):
        return self.source().textures()  # Todo: + TextureMaps from database

    def addTextureMap(self, texture, role=None, external_connection=None):
        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if texture.id() is None:
            TextureMap.addTextureMap(texture, external_connection=connection)

        connection.execute('INSERT INTO texture_material VALUES (:texture_id, :library_id, :role)',
                           {'texture_id': texture.id(), 'role': role, 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()
        return texture

    def libraries(self):
        from ..library import Library

        connection = connect()
        libraries_data = connection.execute('SELECT * FROM library '
                                            'LEFT JOIN material_library ON material_library.library_id = library.id '
                                            'WHERE material_library.material_id = :material_id',
                                            {'library_id': self.id()})
        connection.close()
        return tuple(Library.fromData(data) for data in libraries_data)

    def remove(self, external_connection=None):
        if self.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('DELETE FROM material '
                           'WHERE id = :material_id',
                           {'material_id': self.id()})

        self._id = None

        if external_connection is None:
            connection.commit()
            connection.close()
