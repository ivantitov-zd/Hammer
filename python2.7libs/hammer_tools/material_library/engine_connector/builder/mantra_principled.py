from .material_builder import MaterialBuilder


class MantraPrincipledBuilder(MaterialBuilder):
    def id(self):
        return 'mantra::principled'

    def name(self):
        return 'Principled Shader'

    def createNetwork(self):
        return None

    def createShader(self):
        return self.root_node.createNode('principledshader', self.material_name)

    def __mapPath(self):
        return self.current_map.path(engine=self.engine)

    def addDiffuse(self):
        self.shader_node.parmTuple('basecolor').set((1, 1, 1))
        self.shader_node.parm('basecolor_useTexture').set(True)
        self.shader_node.parm('basecolor_texture').set(self.__mapPath())

    def addRoughness(self):
        self.shader_node.parm('rough').set(1)
        self.shader_node.parm('rough_useTexture').set(True)
        self.shader_node.parm('rough_texture').set(self.__mapPath())

    def addMetalness(self):
        self.shader_node.parm('metallic').set(1)
        self.shader_node.parm('metallic_useTexture').set(True)
        self.shader_node.parm('metallic_texture').set(self.__mapPath())

    def addReflection(self):
        self.shader_node.parm('reflect').set(1)
        self.shader_node.parm('reflect_useTexture').set(True)
        self.shader_node.parm('reflect_texture').set(self.__mapPath())

    def addRefraction(self):
        self.shader_node.parm('transparency').set(1)
        self.shader_node.parm('transparency_useTexture').set(True)
        self.shader_node.parm('transparency_texture').set(self.__mapPath())

    def addNormal(self):
        self.shader_node.parm('baseBumpAndNormal_enable').set(True)
        self.shader_node.parm('baseBumpAndNormal_type').set('normal')
        self.shader_node.parm('baseNormal_texture').set(self.__mapPath())

    def addBump(self):
        self.shader_node.parm('baseBumpAndNormal_enable').set(True)
        self.shader_node.parm('baseBumpAndNormal_type').set('bump')
        self.shader_node.parm('baseBump_bumpTexture').set(self.__mapPath())

    def addSubsurface(self):
        self.shader_node.parm('sss').set(1)
        self.shader_node.parm('sss_useTexture').set(True)
        self.shader_node.parm('sss_texture').set(self.__mapPath())

    def addOpacity(self):
        self.shader_node.parm('opaccolor_useTexture').set(True)
        self.shader_node.parm('opaccolor_texture').set(self.__mapPath())

    def addEmission(self):
        self.shader_node.parm('emitcolor_useTexture').set(True)
        self.shader_node.parm('emitcolor_texture').set(self.__mapPath())

    def addDisplacement(self):
        self.shader_node.parm('dispTex_enable').set(True)
        self.shader_node.parm('dispTex_texture').set(self.__mapPath())
