from ..db import connect
from ..material import Material
from ..texture import TextureMap
from .library import Library


class UnboundLibrary(Library):
    def __init__(self):
        super(UnboundLibrary, self).__init__()

        self._name = 'Unbound'
        self._description = 'Contains items not assigned to any library'
        self._favorite = False

    def materials(self):
        with connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT id, name, comment, favorite, source_path FROM material '
                           'WHERE material.id NOT IN (SELECT material_id FROM material_library)')
            return tuple(Material.fromData(data) for data in cursor.fetchall())

    def textures(self):
        with connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM texture '
                           'WHERE texture.id NOT IN (SELECT texture_id FROM texture_library)')
            return tuple(TextureMap.fromData(data) for data in cursor.fetchall())
