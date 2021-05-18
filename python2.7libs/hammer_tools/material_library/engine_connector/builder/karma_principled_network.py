from .mantra_principled_network import MantraPrincipledNetworkBuilder


class KarmaPrincipledNetworkBuilder(MantraPrincipledNetworkBuilder):
    def id(self):
        return 'karma::principled_network'
