import hou

from ...text import splitAlphaNumeric
from ...texture_map import MapType

DEFAULT_BUILDER_ICON = hou.qt.Icon('MISC_empty', 16, 16)


class MaterialBuilder(object):
    def __init__(self):
        self.material = None
        self.material_name = None
        self.root_node = None
        self.network_node = None
        self.output_node = None
        self.shader_node = None
        self.current_map = None

    def build(self, material, root, name=None):
        self.material = material
        self.material_name = '_'.join(splitAlphaNumeric(name or self.material.name()))
        if isinstance(root, hou.Node):
            self.root_node = root
        else:
            self.root_node = hou.node(root)

        try:
            self.network_node = self.createNetwork()
        except NotImplementedError:
            pass

        self.shader_node = self.createShader()

        for tex_map in self.material.textures():
            self.current_map = tex_map
            method = {
                MapType.Unknown: lambda: None,
                MapType.Thumbnail: lambda: None,
                MapType.Diffuse: self.addDiffuse,
                MapType.Roughness: self.addRoughness,
                MapType.Metalness: self.addMetalness,
                MapType.Reflection: self.addReflection,
                MapType.Refraction: self.addRefraction,
                MapType.Normal: self.addNormal,
                MapType.Bump: self.addBump,
                MapType.Subsurface: self.addSubsurface,
                MapType.Opacity: self.addOpacity,
                MapType.Emission: self.addEmission,
                MapType.Displacement: self.addDisplacement,
                MapType.AmbientOcclusion: self.addAmbientOcclusion
            }[tex_map.type()]
            try:
                method()
            except NotImplementedError:
                continue

        try:
            self.cleanUp()
        except NotImplementedError:
            pass

        return self.network_node or self.shader_node

    def isAvailable(self):
        return True

    def id(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    @staticmethod
    def icon():
        return DEFAULT_BUILDER_ICON

    def createNetwork(self):
        raise NotImplementedError

    def createShader(self):
        raise NotImplementedError

    def cleanUp(self):
        raise NotImplementedError

    def addDiffuse(self):
        raise NotImplementedError

    def addRoughness(self):
        raise NotImplementedError

    def addMetalness(self):
        raise NotImplementedError

    def addReflection(self):
        raise NotImplementedError

    def addRefraction(self):
        raise NotImplementedError

    def addNormal(self):
        raise NotImplementedError

    def addBump(self):
        raise NotImplementedError

    def addSubsurface(self):
        raise NotImplementedError

    def addOpacity(self):
        raise NotImplementedError

    def addEmission(self):
        raise NotImplementedError

    def addDisplacement(self):
        raise NotImplementedError

    def addAmbientOcclusion(self):
        raise NotImplementedError
