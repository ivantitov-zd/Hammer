from ...text import alphaNumericTokens, replaceUDIM, replaceUVTile
from ...map_type import MapType
from .material_builder import MaterialBuilder
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
        shader_node = self.network_node.node('Material1')
        if not shader_node:
            shader_node = self.network_node.createNode('redshift::Material')
        return shader_node

    def setup(self):
        self.shader_node.parm('refl_roughness').set(1)  # Todo: Move to addRoughness?
        self.shader_node.parm('refl_brdf').set('1')  # GGX
        self.shader_node.parm('refl_fresnel_mode').set('2')  # Metalness

        self.output_node = self.network_node.node('redshift_material1')
        self.output_node.setInput(0, self.shader_node)

        self.input_mapping = {
            MapType.Diffuse: self.shader_node.inputIndex('diffuse_color'),
            MapType.Roughness: self.shader_node.inputIndex('refl_roughness'),
            MapType.Metalness: self.shader_node.inputIndex('refl_metalness'),
            MapType.Reflection: self.shader_node.inputIndex('refl_color'),
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

    def __addTexture(self, texture_map=None, name=None, connect_to='shader', linear=True):
        texture_map = texture_map or self.current_map
        name = '_'.join(alphaNumericTokens(name or texture_map.name()))

        texture_node = self.network_node.createNode('redshift::TextureSampler', name)
        tex_map_path = texture_map.path(engine=self.engine)
        uv_mode = self.options.get('uv_mode')
        if uv_mode == 'udim':
            tex_map_path = replaceUDIM(tex_map_path, '<UDIM>')
        elif uv_mode == 'uvtile':
            tex_map_path = replaceUVTile(tex_map_path, '<UVTILE>')
        texture_node.parm('tex0').set(tex_map_path)
        try:  # Fixme: Quick fix for Redshift 3.0.49+
            texture_node.parm('tex0_gammaoverride').set(linear)
        except AttributeError:
            pass

        if connect_to is not None:
            if connect_to == 'shader':
                connect_to = self.shader_node
            connect_to.setInput(self.input_mapping[texture_map.type()], texture_node)
        return texture_node

    def __addColorControl(self, node):
        color_correct_node = self.network_node.createNode('redshift::RSColorCorrection')

        if node.outputConnections():
            connection = node.outputConnections()[0]
            connection.outputNode().setInput(connection.inputIndex(), color_correct_node)

        color_correct_node.setInput(0, node)
        return color_correct_node

    def __addRangeControl(self, node):
        range_correct_node = self.network_node.createNode('redshift::RSMathRange')

        if node.outputConnections():
            connection = node.outputConnections()[0]
            connection.outputNode().setInput(connection.inputIndex(), range_correct_node)

        range_correct_node.setInput(0, node)
        return range_correct_node

    def __addTriPlanar(self, node):
        tri_planar_node = self.network_node.createNode('redshift::TriPlanar')

        if node.outputConnections():
            connection = node.outputConnections()[0]
            connection.outputNode().setInput(connection.inputIndex(), tri_planar_node)

        tri_planar_node.setInput(tri_planar_node.inputIndex('imageX'), node)
        tri_planar_node.setInput(tri_planar_node.inputIndex('imageY'), node)
        tri_planar_node.setInput(tri_planar_node.inputIndex('imageZ'), node)
        return tri_planar_node

    def addDiffuse(self):
        node = self.__addTexture(linear=False)
        if self.options.get('add_color_controls'):
            node = self.__addColorControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addRoughness(self):
        node = self.__addTexture()
        if self.options.get('add_range_controls'):
            node = self.__addRangeControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addGlossiness(self):
        self.addRoughness()
        self.shader_node.parm('relf_isGlossiness').set(True)

    def addMetalness(self):
        node = self.__addTexture()
        if self.options.get('add_range_controls'):
            node = self.__addRangeControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addReflection(self):
        node = self.__addTexture()
        if self.options.get('add_range_controls'):
            node = self.__addRangeControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addRefraction(self):
        node = self.__addTexture()
        if self.options.get('add_range_controls'):
            node = self.__addRangeControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addNormal(self):
        node = self.__addTexture(connect_to=None)

        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.parm('inputType').set('1')  # Tangent-Space Normal
        bump_node.setInput(bump_node.inputIndex('input'), node)

        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addBump(self):
        node = self.__addTexture(connect_to=None)

        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

        bump_node = self.network_node.createNode('redshift::BumpMap')
        bump_node.setInput(bump_node.inputIndex('input'), node)

        self.shader_node.setInput(self.input_mapping[self.current_map.type()], bump_node)

    def addOpacity(self):
        if self.options.get('use_sprite'):
            sprite_node = self.network_node.createNode('redshift::Sprite')
            sprite_node.parm('tex0').set(self.current_map.path(engine=self.engine))
            sprite_node.parm('tex0_gammaoverride').set(True)

            if self.shader_node.outputConnections():
                connection = self.shader_node.outputConnections()[0]
                connection.outputNode().setInput(connection.inputIndex(), sprite_node)
            sprite_node.setInput(sprite_node.inputIndex('input'), self.shader_node)
        else:
            node = self.__addTexture()
            if self.options.get('add_range_controls'):
                node = self.__addRangeControl(node)
            if self.options.get('use_tri_planar'):
                node = self.__addTriPlanar(node)

    def addEmission(self):
        node = self.__addTexture()
        if self.options.get('add_color_controls'):
            node = self.__addColorControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

    def addDisplacement(self):
        node = self.__addTexture(connect_to=None)

        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)

        displacement_node = self.network_node.createNode('redshift::Displacement')
        displacement_node.setInput(displacement_node.inputIndex('texMap'), node)

        self.output_node.setInput(self.input_mapping[self.current_map.type()], displacement_node)

    def addAmbientOcclusion(self):
        node = self.__addTexture()
        if self.options.get('add_range_controls'):
            node = self.__addRangeControl(node)
        if self.options.get('use_tri_planar'):
            node = self.__addTriPlanar(node)
