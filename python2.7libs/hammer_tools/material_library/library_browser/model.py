try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole, FavoriteRole
from ..engine_connector import EngineConnector
from ..material import Material


class MaterialLibraryModel(QAbstractListModel):
    def __init__(self):
        super(MaterialLibraryModel, self).__init__()

        self._library = None
        self._items = ()

    def updateItemList(self):
        if not self._library:
            return

        self.beginResetModel()
        self._items = self._library.items()
        self.endResetModel()

    def library(self):
        return self._library

    def setLibrary(self, library):
        self._library = library
        self.updateItemList()

    def rowCount(self, parent):
        return len(self._items)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._items[row])

    def data(self, index, role):
        if not index.isValid():
            return

        item = index.internalPointer()

        if role == InternalDataRole:
            return item

        if role == Qt.DisplayRole:
            return item.name()
        elif role == Qt.DecorationRole:
            if isinstance(item, Material):
                return item.thumbnail(EngineConnector.currentEngine())
            else:
                return item.thumbnail()
        elif role == FavoriteRole:
            return item.isFavorite()

    def flags(self, index):
        if not index.isValid():
            return

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
