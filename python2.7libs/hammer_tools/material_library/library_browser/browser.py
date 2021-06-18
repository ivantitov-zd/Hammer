try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import QIcon
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import QIcon

from ..material import Material
from ..texture import TextureMap
from ..data_roles import InternalDataRole
from .proxy_model import MaterialLibraryListProxyModel
from .model import MaterialLibraryModel
from .view import LibraryView


class LibraryBrowser(QWidget):
    def __init__(self):
        super(LibraryBrowser, self).__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        main_layout.addLayout(top_layout)

        self.model = MaterialLibraryModel()

        self.proxy_model = MaterialLibraryListProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.view = LibraryView()
        self.view.setIconSize(QSize(64, 64))
        self.view.setModel(self.proxy_model)
        main_layout.addWidget(self.view)

    def reloadContent(self, preserve_selection=True):
        self.model.updateItemList()

    def updateThumbnails(self):
        self.model.dataChanged.emit(self.model.index(0, 0, QModelIndex()),
                                    self.model.index(self.model.rowCount(QModelIndex()) - 1, 0, QModelIndex()),
                                    (Qt.DecorationRole,))

    def hasSelection(self):
        return self.view.selectionModel().hasSelection()

    def currentItem(self):
        return self.view.currentIndex().data(InternalDataRole)

    def selectedMaterials(self):
        items = []
        for index in self.view.selectedIndexes():
            item = index.data(InternalDataRole)
            if isinstance(item, Material):
                items.append(item)
        return tuple(items)

    def selectedTextures(self):
        items = []
        for index in self.view.selectedIndexes():
            item = index.data(InternalDataRole)
            if isinstance(item, TextureMap):
                items.append(item)
        return tuple(items)

    def selectedItems(self):
        return tuple(index.data(InternalDataRole) for index in self.view.selectedIndexes())

    def library(self):
        return self.view.library()

    def setLibrary(self, library):
        self.view.setLibrary(library)
