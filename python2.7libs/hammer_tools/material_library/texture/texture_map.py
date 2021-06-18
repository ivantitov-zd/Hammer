import os
import sqlite3

try:
    from PyQt5.QtGui import QIcon, QPixmap, QImage
except ImportError:
    from PySide2.QtGui import QIcon, QPixmap, QImage

import hou

from ..db import connect
from ..image import imageToBytes
from ..text import alphaNumericTokens
from .map_type import MapType
from .texture_format import TextureFormat

MISSING_TEXTURE_THUMBNAIL_ICON = hou.qt.Icon('BUTTONS_parmmenu_texture', 256, 256)


class ThumbnailState:
    NotLoaded = 0
    Loaded = 1
    NotExists = 2


class TextureMap(object):
    __slots__ = ('_material', '_id', '_name', '_comment', '_favorite', '_options', '_source_path', '_thumbnail_state',
                 '_thumbnail', '_type')

    @staticmethod
    def mapType(name):  # Todo: Move to map type module
        name_tokens = alphaNumericTokens(name.lower())[::-1]
        found_pos = float('+inf')
        found_type = None
        for map_type, tags in MapType.tags().items():
            for tag in tags:
                if tag in name_tokens:
                    pos = name_tokens.index(tag)
                    if pos > found_pos:
                        continue
                    elif pos == found_pos:
                        raise AssertionError('Found intersections between tags in different map types.')
                    found_pos = pos
                    found_type = map_type
                    break
        return found_type or MapType.Unknown

    @staticmethod
    def fromData(data):
        tex = TextureMap(data['name'])
        tex._id = data.get('id')
        tex._comment = data.get('comment')
        tex._favorite = data.get('favorite', False)
        tex._options = data.get('options')
        tex._source_path, _ = os.path.splitext(data['source_path'].replace('\\', '/'))
        return tex

    def asData(self):
        return {
            'name': self.name(),
            'comment': self.comment(),
            'favorite': self.isFavorite(),
            'options': self._options,
            'source_path': self._source_path,
            'thumbnail': sqlite3.Binary(imageToBytes(self._thumbnail)) if self._thumbnail else None
        }

    @staticmethod
    def allTextureMaps():
        connection = connect()
        texture_data = connection.execute('SELECT id, name, comment, favorite, source_path FROM texture').fetchall()
        connection.close()
        return tuple(TextureMap.fromData(data) for data in texture_data)

    @staticmethod
    def addTextureMap(texture, external_connection=None):
        if isinstance(texture, dict):
            texture = TextureMap.fromData(texture)

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        cursor = connection.execute('INSERT INTO texture (name, comment, favorite, options, source_path, thumbnail) '
                                    'VALUES (:name, :comment, :favorite, :options, :source_path, :thumbnail)',
                                    texture.asData())
        texture._id = cursor.lastrowid

        if external_connection is None:
            connection.commit()
            connection.close()
        return texture

    @staticmethod
    def addTexturesFromFolder(path, naming_mode=None, library=None, favorite=False, options=None):
        from ..engine_connector import EngineConnector

        textures = []
        supported_texture_formats = {tex_format for engine in EngineConnector.engines()
                                     for tex_format in engine.supportedTextureFormats()}

        for root, _, files in os.walk(path):
            for file in files:
                name, ext = os.path.splitext(file)
                if TextureMap.mapType(file) == MapType.Unknown and \
                        TextureFormat(ext) in supported_texture_formats:
                    tex = TextureMap.fromData({
                        'name': name,
                        'favorite': favorite,
                        'options': options,
                        'source_path': os.path.join(root, file).replace('\\', '/')
                    })
                    textures.append(tex)

        connection = connect()
        connection.execute('BEGIN')

        if library is not None:
            for tex in textures:
                try:
                    library.addTextureMap(tex, external_connection=connection)
                except sqlite3.IntegrityError:
                    continue
        else:
            for tex in textures:
                try:
                    TextureMap.addTextureMap(tex, external_connection=connection)
                except sqlite3.IntegrityError:
                    continue

        connection.commit()
        connection.close()
        return tuple(tex for tex in textures if tex.id() is not None)

    def __init__(self, name, material=None):
        self._material = material
        self._id = None
        self._name, _ = os.path.splitext(name)
        self._comment = None
        self._favorite = False
        self._options = None
        self._source_path = None
        self._thumbnail_state = ThumbnailState.NotLoaded
        self._thumbnail = None
        self._type = TextureMap.mapType(name)

    def id(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, TextureMap):
            if self.id() and other.id():
                return self.id() == other.id()
            else:
                return self.name() == other.name()  # Todo: Improve
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._name)

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

        connection.execute('UPDATE texture SET favorite = :state WHERE id = :texture_id',
                           {'state': state, 'texture_id': self.id()})

        self._favorite = state

        if external_connection is None:
            connection.commit()
            connection.close()

    def thumbnail(self, reload=False):
        if not self._thumbnail and self._thumbnail_state == ThumbnailState.NotLoaded or reload:
            connection = connect()
            data = connection.execute('SELECT thumbnail AS image FROM texture '
                                      'WHERE id = :texture_id',
                                      {'texture_id': self.id()}).fetchone()
            connection.close()
            if data['image']:
                self._thumbnail = QIcon(QPixmap.fromImage(QImage.fromData(bytes(data['image']), 'png')))
                self._thumbnail_state = ThumbnailState.Loaded
            else:
                self._thumbnail = None
                self._thumbnail_state = ThumbnailState.NotExists

        return self._thumbnail

    def addThumbnail(self, image, external_connection=None):
        if self.id() is None:
            self._thumbnail = image
            return

        image_data = sqlite3.Binary(imageToBytes(image))

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('UPDATE texture SET thumbnail = :image WHERE id = :id',
                           {'id': self.id(), 'image': image_data})

        if external_connection is None:
            connection.commit()
            connection.close()

    def options(self):
        return self._options

    def source(self):
        return self._source_path

    def type(self):
        return self._type

    def formats(self):
        formats = []
        if not self.id() and self._material:
            root_path = self._material.source().path()
            name = self._name
        else:
            root_path, name = os.path.split(self._source_path)

        for file_name in os.listdir(root_path):
            if file_name.startswith(name):
                formats.append(TextureFormat(file_name))
        return tuple(formats)

    def path(self, tex_format=None, engine=None):
        if tex_format and not isinstance(tex_format, TextureFormat):
            tex_format = TextureFormat(tex_format)

        if self._material is None:
            root_dir, name = os.path.split(self._source_path)
        else:
            root_dir = self._material.source().path()
            name = self._name

        if tex_format is not None:
            file_path = os.path.join(root_dir, name + str(tex_format))
        elif engine is not None:
            for target_format in engine.supportedTextureFormats():
                if target_format in self.formats():
                    return self.path(target_format)
            raise ValueError('No suitable texture format found for specified engine.')
        else:
            file_path = os.path.join(root_dir, name + str(self.formats()[0]))
        return file_path.replace('\\', '/')

    def image(self):
        pass

    def __repr__(self):
        return '<{}>'.format(self.name())

    def libraries(self):
        from ..library import Library

        connection = connect()
        libraries_data = connection.execute('SELECT * FROM library '
                                            'LEFT JOIN texture_library ON texture_library.library_id = library.id '
                                            'WHERE texture_library.texture_id = :texture_id',
                                            {'texture_id': self.id()})
        connection.close()
        return tuple(Library.fromData(data) for data in libraries_data)

    def material(self):
        return self._material

    def materials(self):
        from ..material import Material

        connection = connect()
        materials_data = connection.execute('SELECT id, name, comment, favorite, source_path FROM material '
                                            'LEFT JOIN texture_material ON texture_material.material_id = material.id '
                                            'WHERE texture_material.texture_id = :texture_id',
                                            {'texture_id': self.id()})
        connection.close()
        return tuple(Material.fromData(data) for data in materials_data)

    def remove(self, external_connection=None):
        if self.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('DELETE FROM texture '
                           'WHERE id = :texture_id',
                           {'texture_id': self.id()})
        self._id = None

        if external_connection is None:
            connection.commit()
            connection.close()
