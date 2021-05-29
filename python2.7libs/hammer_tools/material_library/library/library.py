from ..db import connect
from ..material import Material, MaterialOptions
from ..texture_map import TextureMap


class Library(object):
    @staticmethod
    def fromData(data):
        lib = Library()
        lib._id = data.get('id')
        lib._name = data['name']
        lib._comment = data.get('comment')
        lib._favorite = data.get('favorite', False)
        lib._options = data.get('options')
        lib._source_path = data.get('source_path')
        return lib

    def asData(self):
        return {
            'id': self.id(),
            'name': self.name(),
            'comment': self.comment(),
            'favorite': self.isFavorite(),
            'options': self._options,
            'source_path': self._source_path
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
        cursor = connection.execute('INSERT INTO library (name, comment, favorite, options, source_path) '
                                    'VALUES (:name, :comment, :favorite, :options, :source_path)',
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
        self._source_path = None

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

        connection.execute('UPDATE library SET favorite = :state WHERE id = :library_id',
                           {'state': state, 'library_id': self.id()})

        self._favorite = state

        if external_connection is None:
            connection.commit()
            connection.close()

    def options(self):
        return MaterialOptions.fromData(self._options)

    def path(self):
        return self._source_path

    def materials(self):
        connection = connect()
        materials_data = connection.execute('SELECT id, name, comment, favorite, source_path FROM material '
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
        return tuple(TextureMap.fromData(data) for data in textures_data)

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

    def addTextureMap(self, texture, external_connection=None):
        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if texture.id() is None:
            TextureMap.addTextureMap(texture, external_connection=connection)

        connection.execute('INSERT INTO texture_library VALUES (:texture_id, :library_id)',
                           {'texture_id': texture.id(), 'library_id': self.id()})

        if external_connection is None:
            connection.commit()
            connection.close()
        return texture

    def addItem(self, item, external_connection=None):
        if isinstance(item, Material):
            self.addMaterial(item, external_connection=external_connection)
        elif isinstance(item, TextureMap):
            self.addTextureMap(item, external_connection=external_connection)
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
        elif isinstance(item, TextureMap):
            self.removeTexture(item, external_connection=external_connection)
        else:
            raise TypeError

    def remove(self, remove_materials=False, only_single_bound_materials=True, external_connection=None):
        if self.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if remove_materials:
            if not only_single_bound_materials:
                connection.execute('DELETE FROM material WHERE id IN ('
                                   'SELECT material_id FROM material_library '
                                   'WHERE library_id = :library_id)',
                                   {'library_id': self.id()})
            else:
                connection.execute('DELETE FROM material WHERE material.id IN ('
                                   'SELECT material_id FROM material_library '
                                   'GROUP BY material_id HAVING count(*) = 1 AND library_id = :library_id)',
                                   {'library_id': self.id()})

        connection.execute('DELETE FROM library WHERE library.id = :library_id',
                           {'library_id': self.id()})

        self._id = None

        if external_connection is None:
            connection.commit()
            connection.close()
