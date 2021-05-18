try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *


class TextureListModel(QAbstractListModel):
    def __init__(self):
        super(TextureListModel, self).__init__()

        self._textures = ()

    def setTextureList(self, textures):
        self.beginResetModel()
        self._textures = tuple(textures)
        self.endResetModel()

    def rowCount(self, parent):
        return len(self._textures)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._textures[row])

    def data(self, index, role):
        if not index.isValid():
            return

        texture = index.internalPointer()

        if role == Qt.UserRole:
            return texture

        if role == Qt.DisplayRole:
            return texture.name()
