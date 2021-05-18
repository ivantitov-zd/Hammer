from ..material import Material
from .library import Library


class AllLibrary(Library):
    def __init__(self):
        super(AllLibrary, self).__init__()

        self._name = 'All'
        self._description = 'Contains all materials'
        self._favorite = False

    def materials(self):
        return Material.allMaterials()
