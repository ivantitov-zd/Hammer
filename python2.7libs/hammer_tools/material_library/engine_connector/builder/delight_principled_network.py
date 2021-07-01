from ...text import alphaNumericTokens
from ...map_type import MapType
from .material_builder import MaterialBuilder


class ColorToFloatMode:
    Luminance = 0
    Average = 1
    Add = 2
    Min = 3
    Max = 4
    Red = 5
    Green = 6
    Blue = 7


class BumpDisplacementType:
    Bump = 0
    NormalDirectX = 1
    NormalOpenGL = 2
    Displacement0Centered = 3
    Displacement05Centered = 4


class DelightPrincipledBuilder(MaterialBuilder):
    def id(self):
        return '3delight::network'

    def name(self):
        return 'Principled Network'

    def createNetwork(self):
        return self.root_node.createNode('3Delight::dlMaterialBuilder', self.material_name)

    def createShader(self):
        shader_node = self.network_node.node('dlPrincipled1')
        if not shader_node:
            shader_node = self.network_node.createNode('3Delight::dlPrincipled')
        return shader_node

    def setup(self):
        self.output_node = self.network_node.node('dlTerminal1')
        self.output_node.setInput(0, self.shader_node)

        self.input_mapping = {
            MapType.Diffuse: self.shader_node.inputIndex('i_color'),
            MapType.Roughness: self.shader_node.inputIndex('roughness'),
            MapType.Metalness: self.shader_node.inputIndex('metallic'),
            MapType.Reflection: None,
            MapType.Refraction: self.shader_node.inputIndex('volumetric_transparency_color'),
            MapType.Normal: self.shader_node.inputIndex('disp_normal_bump_value'),
            MapType.Bump: self.shader_node.inputIndex('disp_normal_bump_value'),
            MapType.Subsurface: None,  # Todo
            MapType.Opacity: self.shader_node.inputIndex('opacity'),
            MapType.Emission: self.shader_node.inputIndex('incandescence'),
            MapType.Displacement: self.output_node.inputIndex('Displacement')
        }

    def cleanup(self):
        self.network_node.layoutChildren()

    def __addTexture(self, texture_map=None, name=None, connect_to='shader', linear=True):
        texture_map = texture_map or self.current_map
        name = '_'.join(alphaNumericTokens(name or texture_map.name()))

        texture_node = self.network_node.createNode('3Delight::dlTexture', name)
        tex_map_path = texture_map.path(engine=self.engine)
        texture_node.parm('textureFile').set(tex_map_path)

        if connect_to is not None:
            if connect_to == 'shader':
                connect_to = self.shader_node
            connect_to.setInput(self.input_mapping[texture_map.type()], texture_node)
        return texture_node

    def __addColorToFloat(self, add_to, output_index=0, mode=ColorToFloatMode.Luminance):
        color_to_float_node = self.network_node.createNode('3Delight::dlColorToFloat')
        color_to_float_node.parm('mode').set(mode)

        if add_to.outputConnections():
            connection = add_to.outputConnections()[output_index]
            connection.outputNode().setInput(connection.inputIndex(), color_to_float_node)
        color_to_float_node.setInput(1, add_to, output_index)
        return color_to_float_node

    def addDiffuse(self):
        node = self.__addTexture(linear=False)

    def addRoughness(self):
        node = self.__addTexture()
        node = self.__addColorToFloat(node)

    def addMetalness(self):
        node = self.__addTexture()
        node = self.__addColorToFloat(node)

    def addRefraction(self):
        node = self.__addTexture()

    def addNormal(self):
        self.shader_node.parm('disp_normal_bump_type').set(BumpDisplacementType.NormalOpenGL)  # Todo
        node = self.__addTexture()

    def addBump(self):
        self.shader_node.parm('disp_normal_bump_type').set(BumpDisplacementType.Bump)
        node = self.__addTexture()

    def addOpacity(self):
        node = self.__addTexture()
        node = self.__addColorToFloat(node)

    def addEmission(self):
        node = self.__addTexture()

    def addDisplacement(self):
        node = self.__addTexture(connect_to=None)
        node = self.__addColorToFloat(node)

        displacement_node = self.network_node.createNode('3Delight::dlDisplacement')
        displacement_node.parm('scalarScale').set(0.05)
        displacement_node.parm('scalarCenter').set(-0.5)
        displacement_node.setInput(displacement_node.inputIndex('scalarDisplacement'), node)

        self.output_node.setInput(self.input_mapping[self.current_map.type()], displacement_node)
