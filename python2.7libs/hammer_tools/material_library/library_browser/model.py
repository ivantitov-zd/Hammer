import os

from ..map_type import MapType

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole, FavoriteRole, TextForFilterRole
from ..engine_connector import EngineConnector
from ..material import Material, MISSING_MATERIAL_THUMBNAIL_ICON
from ..texture import Texture, MISSING_TEXTURE_THUMBNAIL_ICON
from ..tooltip_formlayout import ToolTipFormLayout


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

    def rowCount(self, parent=None):
        return len(self._items)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._items[row])

    def flags(self, index):
        if not index.isValid():
            return

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if isinstance(index.internalPointer(), Texture):
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
            tooltip = ToolTipFormLayout()
            tooltip.addRow('<b>Type</b>', 'Material' if isinstance(item, Material) else 'Texture')
            tooltip.addRow('<b>ID</b>', item.id())
            tooltip.addRow('<b>Name</b>', item.name())
            if isinstance(item, Material):
                tooltip.addRow('<b>Path</b>', item.path() or None)
                tooltip.addRow('<b>Map types</b>', ' '.join(MapType.typeName(tex.type()) for tex in item.textures()))
            elif isinstance(item, Texture):
                tooltip.addRow('<b>Path</b>', os.path.splitext(item.path())[0])
                tooltip.addRow('<b>Formats</b>', ' '.join(map(str, item.formats())))
            return str(tooltip)
        elif role == TextForFilterRole:
            return item.name() + item.comment()

    def mimeData(self, indexes):
        data = QMimeData()
        current_item = indexes[-1].data(InternalDataRole)
        data.setText(current_item.path(engine=EngineConnector.currentEngine()))
        return data
