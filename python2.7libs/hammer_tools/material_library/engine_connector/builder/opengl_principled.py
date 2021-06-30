from .material_builder import MaterialBuilder


class OpenGLPrincipledBuilder(MaterialBuilder):
    def id(self):
        return 'opengl::principled'

    def name(self):
        return 'Principled Shader'

    def createShader(self):
        return self.root_node.createNode('null', self.material_name)
