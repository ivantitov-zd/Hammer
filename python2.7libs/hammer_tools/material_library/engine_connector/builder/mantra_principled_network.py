from .material_builder import MaterialBuilder


class MantraPrincipledNetworkBuilder(MaterialBuilder):
    def id(self):
        return 'mantra::principled_network'

    def name(self):
        return 'Principled Shader Network'

    def createNetwork(self):
        return self.root_node.createNode('materialbuilder', self.material_name)

    def createShader(self):
        return self.network_node.createNode('principledshader')
