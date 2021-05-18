from ...text import splitAlphaNumeric
from ...texture_map import MapType
from .builder import MaterialBuilder


class RedshiftNetworkBuilder(MaterialBuilder):
    def id(self):
        return 'redshift::network'

    def name(self):
        return 'Network'

    def createNetwork(self):
        network_node = self.root_node.createNode('redshift_vopnet', self.material_name)
        self.output_node = network_node.node('redshift_material1')
        return network_node

    def createShader(self):
        shader_node = self.network_node.createNode('redshift::Material')
        shader_node.parm('refl_roughness').set(1)  # Todo: Remove
        shader_node.parm('refl_brdf').set('1')  # GGX
        shader_node.parm('refl_fresnel_mode').set('2')  # Metalness

        self.input_mapping = {
            MapType.Diffuse: shader_node.inputIndex('diffuse_color'),
            MapType.Roughness: shader_node.inputIndex('refl_roughness'),
            MapType.Metalness: shader_node.inputIndex('refl_metalness'),
            MapType.Reflection: shader_node.inputIndex('relf_color'),
            MapType.Refraction: shader_node.inputIndex('refr_color'),
            MapType.Normal: shader_node.inputIndex('bump_input'),
            MapType.Bump: shader_node.inputIndex('bump_input'),
            MapType.Subsurface: None,
            MapType.Opacity: shader_node.inputIndex('opacity_color'),
            MapType.Emission: shader_node.inputIndex('emission_color'),
            MapType.Displacement: self.output_node.inputIndex('Displacement'),
            MapType.AmbientOcclusion: shader_node.inputIndex('diffuse_weight')
        }

        self.output_node.setInput(0, shader_node)
        return shader_node

    def cleanUp(self):
        self.network_node.layoutChildren()

    def addTexture(self, texture_map, name=None, raw=True):
        name = '_'.join(splitAlphaNumeric(name or texture_map.name()))
        texture_node = self.network_node.createNode('redshift::TextureSampler', name)
        texture_node.parm('tex0').set(texture_map.path())
        texture_node.parm('tex0_gammaoverride').set(raw)
        return texture_node

    def addDiffuse(self):
        texture_node = self.addTexture(self.current_map, raw=False)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addRoughness(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addMetalness(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addReflection(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addRefraction(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addNormal(self):
        texture_node = self.addTexture(self.current_map)

        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.parm('inputType').set('1')  # Tangent-Space Normal
        bump_node.setInput(0, texture_node)

        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addBump(self):
        texture_node = self.addTexture(self.current_map)

        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.setInput(0, texture_node)

        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addOpacity(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addEmission(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)

    def addDisplacement(self):
        texture_node = self.addTexture(self.current_map)

        displacement_node = self.network_node.createNode('redshift::Displacement')
        displacement_node.setInput(0, texture_node)

        self.output_node.setInput(self.input_mapping[self.current_map.type()], displacement_node)

    def addAmbientOcclusion(self):
        texture_node = self.addTexture(self.current_map)
        self.shader_node.setInput(self.input_mapping[self.current_map.type()], texture_node)
