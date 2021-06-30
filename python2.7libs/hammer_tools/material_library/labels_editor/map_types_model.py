try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole
from ..map_type import MapType


class MapTypesModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(MapTypesModel, self).__init__(parent)

        self._map_types = MapType.allTypes()
        self._map_type_names = {t: MapType.typeName(t) for t in MapType.allTypes()}

    def rowCount(self, parent):
        return len(self._map_types)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._map_types[row])

    def data(self, index, role):
        if not index.isValid():
            return

        map_type = index.internalPointer()

        if role == InternalDataRole:
            return map_type

        if role == Qt.DisplayRole:
            return self._map_type_names[map_type]
        elif role == Qt.ToolTipRole:
            return map_type
