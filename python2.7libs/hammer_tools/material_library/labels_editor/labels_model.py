try:
    from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
except ImportError:
    from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt

from ..data_roles import InternalDataRole
from ..map_type import MapType


class LabelsModel(QAbstractListModel):
    def __init__(self, changes, parent=None):
        super(LabelsModel, self).__init__(parent)

        self._map_type = None
        self._changes = changes
        self._labels = ()
        self._delete = []
        self._renaming = {}
        self._new = []

    def updateLabelsList(self):
        if not self._map_type:
            return

        self.beginResetModel()
        self._labels = self._changes[self._map_type]['labels']
        self._delete = self._changes[self._map_type]['delete']
        self._new = self._changes[self._map_type]['new']
        self._renaming = self._changes[self._map_type]['renaming']
        self.endResetModel()

    def mapType(self):
        return self._map_type

    def setMapType(self, map_type):
        self._map_type = map_type
        self.updateLabelsList()

    def rowCount(self, parent):
        return len(self._labels) + len(self._new)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if row < len(self._labels):
            source = self._labels
        else:
            source = self._new
        return self.createIndex(row, column, source[row - len(self._labels)])

    def flags(self, index):
        if not index.isValid():
            return

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role):
        if not index.isValid():
            return

        label = index.internalPointer()

        if role == InternalDataRole:
            return label

        if role == Qt.DisplayRole:
            prefix = ''
            suffix = ''
            if label in self._delete:
                prefix = 'Delete: '
            elif label in self._new:
                prefix = 'New: '
            elif label in self._renaming:
                prefix = 'Rename: '
                suffix = ' -> ' + self._renaming[label]
            return prefix + label + suffix
        elif role == Qt.EditRole:
            if label in self._renaming:
                return self._renaming[label]
            else:
                return label

    def cancelChanges(self):
        self.beginResetModel()
        self._changes[self._map_type]['delete'] = []
        self._changes[self._map_type]['new'] = []
        self._changes[self._map_type]['renaming'] = {}
        self.updateLabelsList()
        self.endResetModel()

    def addRow(self):
        count = self.rowCount(QModelIndex())
        self.beginInsertRows(QModelIndex(), count, count)
        self._new.append('')
        self.endInsertRows()
        return True

    def removeRow(self, row):
        if row < len(self._labels):
            label = self._labels[row]
            self._delete.append(label)
            self.dataChanged.emit(self.index(row, 0, QModelIndex()),
                                  self.index(row, 0, QModelIndex()),
                                  [Qt.DisplayRole])
            return False
        else:
            self.beginRemoveRows(QModelIndex(), row, row)
            row -= len(self._labels)
            self._new.pop(row)
            self.endRemoveRows()
            return True

    def setData(self, index, value, role):
        if not index.isValid():
            return

        if not value.strip():
            return False

        label = index.data(InternalDataRole)
        if label in self._labels:
            if label == value:
                self._renaming.pop(label, None)
                self.dataChanged.emit(index, index, [role])
                return True

            if value in self._labels or value in self._renaming.values():
                return False

            self._renaming[label] = value
            if label in self._delete:
                self._delete.pop(self._delete.index(label))
        else:
            if value in self._labels or value in self._renaming.values():
                return False

            self._new[self._new.index(label)] = value
        self.dataChanged.emit(index, index, [role])
        return True
