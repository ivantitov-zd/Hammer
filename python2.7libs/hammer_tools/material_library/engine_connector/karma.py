import hou

from .engine_connector import EngineConnector
from .mantra import MantraConnector
from .builder import KarmaPrincipledBuilder


class KarmaConnector(MantraConnector):
    def __init__(self):
        super(KarmaConnector, self).__init__()

    def isAvailable(self):
        major_version, minor_version, build_version = hou.applicationVersion()
        return major_version >= 18

    def id(self):
        return 'karma::1'

    def name(self):
        return 'Karma'

    def icon(self):
        return hou.qt.Icon('MISC_karma', 16, 16)

    def nodeTypeAssociatedWithEngine(self, node_type):
        if 'karma' in node_type.description().lower():
            return True

        return super(KarmaConnector, self).nodeTypeAssociatedWithEngine(node_type)

    def builders(self):
        return KarmaPrincipledBuilder(self),


EngineConnector.registerEngine(KarmaConnector)
