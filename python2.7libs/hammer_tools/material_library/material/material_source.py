import os

from ..texture_map import TextureMap, MapType


class MaterialSource(object):
    def __init__(self, material, path):
        self._material = material
        self._path = path

    def material(self):
        return self._material

    def path(self):
        return self._path

    def textures(self):  # Todo: Pick up thumbnails
        textures = []
        for file_name in os.listdir(self.path()):
            tex = TextureMap(file_name, self._material)
            if tex.type not in {MapType.Unknown, MapType.Thumbnail}:
                textures.append(tex)
        return tuple(set(textures))
