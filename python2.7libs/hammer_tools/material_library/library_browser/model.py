try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole, FavoriteRole
from ..engine_connector import EngineConnector


class MaterialLibraryModel(QAbstractListModel):
    def __init__(self):
        super(MaterialLibraryModel, self).__init__()

        self._library = None
        self._materials = ()

    def updateMaterialList(self):
        if not self._library:
            return

        self.beginResetModel()
        self._materials = self._library.materials()
        self.endResetModel()

    def library(self):
        return self._library

    def setLibrary(self, library):
        self._library = library
        self.updateMaterialList()

    def rowCount(self, parent):
        return len(self._materials)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._materials[row])

    def data(self, index, role):
        if not index.isValid():
            return

        material = index.internalPointer()

        if role == InternalDataRole:
            return material

        if role == Qt.DisplayRole:
            return material.name()
        elif role == Qt.DecorationRole:
            return material.thumbnail(EngineConnector.currentEngine())
        elif role == FavoriteRole:
            return material.isFavorite()

    def flags(self, index):
        if not index.isValid():
            return

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
