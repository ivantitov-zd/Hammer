from ..db.connect import connect
from ..material import Material
from .library import Library


class UnboundLibrary(Library):
    def __init__(self):
        super(UnboundLibrary, self).__init__()

        self._name = 'Unbound'
        self._description = 'Contains materials not assigned to libraries'
        self._favorite = False

    def materials(self):
        with connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT id, name, comment, favorite, source_path FROM material '
                           'WHERE material.id NOT IN (SELECT material_id FROM material_library)')
            return tuple(Material.fromData(data) for data in cursor.fetchall())
