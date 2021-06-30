from ..db import connect
from ..material import Material
from ..texture import Texture


class Library(object):
    __slots__ = ('_id', '_name', '_comment', '_favorite', '_options', '_path')

    def fillFromData(self, data):
        self._id = data.get('id')
        self._name = data['name']
        self._comment = data.get('comment')
        self._favorite = data.get('favorite', False)
        self._options = data.get('options')
        self._path = data.get('path')

    @staticmethod
    def fromData(data):
        lib = Library()
        lib.fillFromData(data)
        return lib

    def asData(self):
        return {
            'id': self.id(),
            'name': self.name(),
            'comment': self.comment() or None,
            'favorite': self.isFavorite(),
            'options': self._options or None,
            'path': self._path
        }

    @staticmethod
    def allLibraries():
        connection = connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM library')
        return tuple(Library.fromData(data) for data in cursor.fetchall())

    @staticmethod
    def addLibrary(library):
        if isinstance(library, dict):
            library = Library.fromData(library)

        connection = connect()
        cursor = connection.execute('INSERT INTO library (name, comment, favorite, options, path) '
                                    'VALUES (:name, :comment, :favorite, :options, :path)',
                                    library.asData())
        library._id = cursor.lastrowid

        connection.commit()
        connection.close()
        return library

    def __init__(self):
        self._id = None
        self._name = None
        self._comment = None
        self._favorite = False
        self._options = None
        self._path = None

    def id(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, Library):
            if self.id() and other.id():
                return self.id() == other.id()
            else:
                pass  # Todo: Compare attributes
        else:
            return NotImplemented

    def name(self):
        return self._name

    def comment(self):
        return self._comment or ''

    def isFavorite(self):
        return self._favorite

    def markAsFavorite(self, state=True, external_connection=None):
        if state is None:
            state = not self._favorite

        self._favorite = state

        if self.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('UPDATE library SET favorite = :state WHERE id = :library_id',
                           {'state': state, 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()

    def options(self):
        return self._options or {}

    def path(self):
        return self._path

    def materials(self):
        connection = connect()
        materials_data = connection.execute('SELECT id, name, comment, favorite, path FROM material '
                                            'LEFT JOIN material_library ON material_library.material_id = material.id '
                                            'WHERE material_library.library_id = :library_id',
                                            {'library_id': self.id()}).fetchall()
        return tuple(Material.fromData(data) for data in materials_data)

    def textures(self):
        connection = connect()
        textures_data = connection.execute('SELECT * FROM texture '
                                           'LEFT JOIN texture_library ON texture_library.texture_id = texture.id '
                                           'WHERE texture_library.library_id = :library_id',
                                           {'library_id': self.id()}).fetchall()
        connection.close()
        return tuple(Texture.fromData(data) for data in textures_data)

    def items(self):
        return self.materials() + self.textures()

    def addMaterial(self, material, external_connection=None):
        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if material.id() is None:
            Material.addMaterial(material, external_connection=connection)

        connection.execute('INSERT INTO material_library VALUES (:material_id, :library_id)',
                           {'material_id': material.id(), 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()
        return material

    def addTexture(self, texture, external_connection=None):
        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if texture.id() is None:
            Texture.addTexture(texture, external_connection=connection)

        connection.execute('INSERT INTO texture_library VALUES (:texture_id, :library_id)',
                           {'texture_id': texture.id(), 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()
        return texture

    def addItem(self, item, external_connection=None):
        if isinstance(item, Material):
            self.addMaterial(item, external_connection=external_connection)
        elif isinstance(item, Texture):
            self.addTexture(item, external_connection=external_connection)
        else:
            raise TypeError

    def removeMaterial(self, material, external_connection=None):
        if material.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('DELETE FROM material_library '
                           'WHERE material_id = :material_id AND library_id = :library_id',
                           {'material_id': material.id(), 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()

    def removeTexture(self, texture, external_connection=None):
        if texture.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('DELETE FROM texture_library '
                           'WHERE texture_id = :texture_id AND library_id = :library_id',
                           {'texture_id': texture.id(), 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()

    def removeItem(self, item, external_connection=None):
        if isinstance(item, Material):
            self.removeMaterial(item, external_connection=external_connection)
        elif isinstance(item, Texture):
            self.removeTexture(item, external_connection=external_connection)
        else:
            raise TypeError

    def remove(self, remove_materials=False, only_single_bound_materials=True,
               remove_textures=False, only_single_bound_textures=True,
               external_connection=None):
        if self.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if remove_materials:
            if only_single_bound_materials:
                connection.execute('DELETE FROM material WHERE material.id IN ('
                                   'SELECT material_id FROM material_library '
                                   'GROUP BY material_id HAVING count(*) = 1 AND library_id = :library_id)',
                                   {'library_id': self.id()})

            else:
                connection.execute('DELETE FROM material WHERE id IN ('
                                   'SELECT material_id FROM material_library '
                                   'WHERE library_id = :library_id)',
                                   {'library_id': self.id()})

        if remove_textures:
            if only_single_bound_textures:
                connection.execute('DELETE FROM texture WHERE texture.id IN ('
                                   'SELECT texture_id FROM texture_library '
                                   'GROUP BY texture_id HAVING count(*) = 1 AND library_id = :library_id)',
                                   {'library_id': self.id()})
            else:
                connection.execute('DELETE FROM texture WHERE id IN ('
                                   'SELECT texture_id FROM texture_library '
                                   'WHERE library_id = :library_id)',
                                   {'library_id': self.id()})

        connection.execute('DELETE FROM library WHERE library.id = :library_id',
                           {'library_id': self.id()})

        self._id = None

        if external_connection is None:
            connection.commit()
            connection.close()
