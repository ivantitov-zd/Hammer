import hou

DEFAULT_ENGINE_ICON = hou.qt.Icon('COMMON_engine', 16, 16)


class EngineConnector(object):
    __engines = []
    __current_engine = None

    @staticmethod
    def registerEngine(engine):
        EngineConnector.__engines.append(engine())

    @staticmethod
    def engines():
        return tuple(EngineConnector.__engines)

    @staticmethod
    def setCurrentEngine(engine):
        EngineConnector.__current_engine = engine

    @staticmethod
    def currentEngine():
        if EngineConnector.__current_engine is not None:
            return EngineConnector.__current_engine
        else:
            ipr_pane_tab = hou.ui.paneTabOfType(hou.paneTabType.IPRViewer)

            if not ipr_pane_tab:
                return

            rop_node = ipr_pane_tab.ropNode()
            if rop_node is None:
                return

            for engine in EngineConnector.__engines:
                if engine.nodeTypeAssociatedWithEngine(rop_node.type()):
                    return engine

    def isAvailable(self):
        raise NotImplementedError

    def id(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    @staticmethod
    def icon():
        return DEFAULT_ENGINE_ICON

    def nodeTypeAssociatedWithEngine(self, node_type):
        raise NotImplementedError

    @staticmethod
    def builders():
        return ()

    def supportedTextureFormats(self):
        raise NotImplementedError

    def isValidTextureFormat(self, tex_format):
        return tex_format in self.supportedTextureFormats()
