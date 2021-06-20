try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole, FavoriteRole
from ..engine_connector import EngineConnector
from ..material import Material, MISSING_MATERIAL_THUMBNAIL_ICON
from ..texture import TextureMap, MISSING_TEXTURE_THUMBNAIL_ICON


class MaterialLibraryModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(MaterialLibraryModel, self).__init__(parent)

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

    def flags(self, index):
        if not index.isValid():
            return

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if isinstance(index.internalPointer(), TextureMap):
            return flags | Qt.ItemIsDragEnabled
        return flags

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
                thumbnail = item.thumbnail(EngineConnector.currentEngine())
                return thumbnail or MISSING_MATERIAL_THUMBNAIL_ICON
            else:
                thumbnail = item.thumbnail()
                return thumbnail or MISSING_TEXTURE_THUMBNAIL_ICON
        elif role == FavoriteRole:
            return item.isFavorite()
        elif role == Qt.ToolTipRole:
            tooltip = '<p style="white-space:pre">'
            tooltip += '<b>Type</b>  <i>{}</i>\n'.format('Material'
                                                         if isinstance(item, Material)
                                                         else 'Texture')
            tooltip += '<b>ID</b>  <i>{}</i>\n'.format(item.id())
            tooltip += '<b>Name</b>  <i>{}</i>\n'.format(item.name())
            tooltip += '<b>Path</b>  <i>{}</i>\n'.format(item.path())
            if isinstance(item, TextureMap):
                tooltip += '<b>Formats</b>  <i>{}</i>'.format(' '.join(map(str, item.formats())))
            tooltip += '</p>'
            return tooltip

    def mimeData(self, indexes):
        data = QMimeData()
        current_item = indexes[-1].data(InternalDataRole)
        data.setText(current_item.path(engine=EngineConnector.currentEngine()))
        return data
