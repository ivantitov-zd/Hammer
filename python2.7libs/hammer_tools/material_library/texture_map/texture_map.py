import os

from ..text import splitAlphaNumeric
from .map_type import MapType
from .texture_format import TextureFormat


class TextureMap(object):
    @staticmethod
    def fromData(data):
        pass

    def asData(self):
        pass

    @staticmethod
    def mapType(name):
        name_tags = splitAlphaNumeric(name.lower())

        for map_type, tags in MapType.tags().items():
            for tag in tags:
                if tag in name_tags:
                    return map_type
        return MapType.Unknown

    def __init__(self, name, material=None):
        self._material = material
        self._name, _ = os.path.splitext(name)
        self._type = TextureMap.mapType(name)

        formats = []
        for file_name in os.listdir(material.source().path()):
            if file_name.startswith(name):
                formats.append(TextureFormat(file_name))
        self._formats = tuple(formats)

    def material(self):
        return self._material

    def name(self):
        return self._name

    def thumbnail(self):
        pass

    def type(self):
        return self._type

    def formats(self):
        return self._formats

    def path(self, tex_format=None, engine=None):
        material_dir = self._material.source().path()
        if tex_format is not None:
            file_path = os.path.join(material_dir, self._name + str(tex_format))
        elif engine is not None:
            for target_format in engine.supportedTextureFormats():
                if target_format in self._formats:
                    return self.path(target_format)
            raise ValueError('No suitable texture format found for specified engine.')
        else:
            file_path = os.path.join(material_dir, self._name + str(self._formats[0]))
        return file_path.replace('\\', '/')
