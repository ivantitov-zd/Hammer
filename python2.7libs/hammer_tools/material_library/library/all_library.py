from ..material import Material
from ..texture import Texture
from .library import Library
from .polyhaven_library import PolyHavenLibrary


class AllLibrary(Library):
    def __init__(self):
        super(AllLibrary, self).__init__()

        self._name = 'All'
        self._comment = 'Contains all items'
        self._favorite = True

    def materials(self):
        mats = Material.allMaterials()
        try:
            mats += PolyHavenLibrary().materials()
        except Exception:
            pass
        return mats

    def textures(self):
        return Texture.allTextures()
