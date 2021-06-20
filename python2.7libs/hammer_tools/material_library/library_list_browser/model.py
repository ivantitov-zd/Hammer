try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole
from ..library import Library, AllLibrary, UnboundLibrary


class LibraryListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(LibraryListModel, self).__init__(parent)

        self._libraries = ()

    def updateLibraryList(self):
        self.beginResetModel()
        self._libraries = (AllLibrary(), UnboundLibrary())
        self._libraries += Library.allLibraries()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self._libraries)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._libraries[row])

    def data(self, index, role):
        if not index.isValid():
            return

        library = index.internalPointer()

        if role == InternalDataRole:
            return library

        if role == Qt.DisplayRole:
            return library.name()
        elif role == Qt.ToolTipRole:
            return library.comment()
