from ...text import splitAlphaNumeric
from ...texture_map import MapType
from .builder import MaterialBuilder
from .redshift_options import RedshiftBuildOptions


class RedshiftNetworkBuilder(MaterialBuilder):
    def id(self):
        return 'redshift::network'

    def name(self):
        return 'Network'

    def buildOptionsWidget(self):
        return RedshiftBuildOptions()

    def createNetwork(self):
        return self.root_node.createNode('redshift_vopnet', self.material_name)

    def createShader(self):
        shader_node = self.network_node.createNode('redshift::Material')
        shader_node.parm('refl_roughness').set(1)  # Todo: Move to addRoughness?
        shader_node.parm('refl_brdf').set('1')  # GGX
        shader_node.parm('refl_fresnel_mode').set('2')  # Metalness
        return shader_node

    def setup(self):
        self.output_node = self.network_node.node('redshift_material1')
        self.output_node.setInput(0, self.shader_node)

        self.input_mapping = {
            MapType.Diffuse: self.shader_node.inputIndex('diffuse_color'),
            MapType.Roughness: self.shader_node.inputIndex('refl_roughness'),
            MapType.Metalness: self.shader_node.inputIndex('refl_metalness'),
            MapType.Reflection: self.shader_node.inputIndex('relf_color'),
            MapType.Refraction: self.shader_node.inputIndex('refr_color'),
            MapType.Normal: self.shader_node.inputIndex('bump_input'),
            MapType.Bump: self.shader_node.inputIndex('bump_input'),
            MapType.Subsurface: None,
            MapType.Opacity: self.shader_node.inputIndex('opacity_color'),
            MapType.Emission: self.shader_node.inputIndex('emission_color'),
            MapType.Displacement: self.output_node.inputIndex('Displacement'),
            MapType.AmbientOcclusion: self.shader_node.inputIndex('diffuse_weight')
        }

    def cleanup(self):
        self.network_node.layoutChildren()

    def __addTexture(self, texture_map=None, name=None, connect_to=None, raw=True):
        texture_map = texture_map or self.current_map
        name = '_'.join(splitAlphaNumeric(name or texture_map.name()))

        texture_node = self.network_node.createNode('redshift::TextureSampler', name)
        texture_node.parm('tex0').set(texture_map.path())
        texture_node.parm('tex0_gammaoverride').set(raw)

        if connect_to is None:
            connect_to = self.shader_node
        connect_to.setInput(self.input_mapping[texture_map.type()], texture_node)
        return texture_node

    def __addTriPlanar(self, texture_node):
        tri_planar_node = self.network_node.createNode('redshift::TriPlanar')
        if texture_node.outputConnections():
            connection = texture_node.outputConnections()[0]
            connection.outputNode().setInput(connection.inputIndex(), tri_planar_node)

        tri_planar_node.setInput(tri_planar_node.inputIndex('imageX'), texture_node)
        tri_planar_node.setInput(tri_planar_node.inputIndex('imageY'), texture_node)
        tri_planar_node.setInput(tri_planar_node.inputIndex('imageZ'), texture_node)
        return tri_planar_node

    def addDiffuse(self):
        node = self.__addTexture(raw=False)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addRoughness(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addMetalness(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addReflection(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addRefraction(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addNormal(self):
        texture_node = self.__addTexture()
        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.parm('inputType').set('1')  # Tangent-Space Normal
        bump_node.setInput(0, texture_node)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addBump(self):
        texture_node = self.__addTexture()
        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.setInput(0, texture_node)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addOpacity(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addEmission(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addDisplacement(self):
        texture_node = self.__addTexture()
        displacement_node = self.network_node.createNode('redshift::Displacement')
        displacement_node.setInput(0, texture_node)
        self.output_node.setInput(self.input_mapping[self.current_map.type()], displacement_node)

    def addAmbientOcclusion(self):
        node = self.__addTexture()
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)
