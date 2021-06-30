try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from .data_roles import InternalDataRole


class MaterialBindingsWidget(QWidget):
    def __init__(self, parent=None):
        super(MaterialBindingsWidget, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.model = LibraryListModel(self)
        self.proxy_model = CheckableProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.view = LibraryListView()
        self.view.setModel(self.proxy_model)

    # def boundLibraries(self):
    #     libraries = []
    #     for i in range(self.proxy_model.rowCount()):
    #         index = self.proxy_model.index(i, 0)
    #         if index.data(Qt.CheckStateRole):
    #             libraries.append(index.data(InternalDataRole))
    #     return tuple(libraries)
