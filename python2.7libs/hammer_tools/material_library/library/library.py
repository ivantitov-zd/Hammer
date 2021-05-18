from ..db.connect import connect
from ..material import Material, MaterialOptions


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
            'id': self._id,
            'name': self._name,
            'comment': self._comment,
            'favorite': self._favorite,
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

    def name(self):
        return self._name

    def comment(self):
        return self._comment

    def isFavorite(self):
        return self._favorite

    def options(self):
        return MaterialOptions.fromData(self._options)

    def path(self):
        return self._source_path

    def materials(self):
        with connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM material '
                           'LEFT JOIN material_library ON material_library.material_id = material.id '
                           'WHERE material_library.library_id = :library_id',
                           {'library_id': self._id})
            return tuple(Material.fromData(data) for data in cursor.fetchall())

    def addMaterial(self, material, external_connection=None):
        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if material.id() is None:
            Material.addMaterial(material, external_connection)

        connection.execute('INSERT INTO material_library VALUES (:material_id, :library_id)',
                           {'material_id': material.id(), 'library_id': self._id})

        if external_connection is None:
            connection.commit()
            connection.close()

        return material

    def removeMaterial(self, material, external_connection=None):
        if material.id() is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        connection.execute('DELETE FROM material_library '
                           'WHERE material_id = :material_id AND library_id = :library_id',
                           {'material_id': material.id(), 'library_id': self._id})

        if external_connection is None:
            connection.commit()
            connection.close()

    def remove(self, remove_materials=False, only_single_bound_materials=True, external_connection=None):
        if self._id is None:
            return

        if external_connection is None:
            connection = connect()
        else:
            connection = external_connection

        if remove_materials:
            if not only_single_bound_materials:
                connection.execute('DELETE FROM material WHERE library_id = :library_id',
                                   {'library_id': self._id})
            else:
                connection.execute('DELETE FROM material WHERE material.id IN ('
                                   'SELECT material_id FROM material_library '
                                   'GROUP BY material_id HAVING count(*) = 1 AND library_id = :library_id)',
                                   {'library_id': self._id})

        connection.execute('DELETE FROM library WHERE library.id = :library_id',
                           {'library_id': self._id})

        self._id = None

        if external_connection is None:
            connection.commit()
            connection.close()
