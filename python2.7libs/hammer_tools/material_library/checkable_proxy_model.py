try:
    from PyQt5.QtCore import QIdentityProxyModel, QModelIndex, Qt
except ImportError:
    from PySide2.QtCore import QIdentityProxyModel, QModelIndex, Qt


class CheckableProxyModel(QIdentityProxyModel):
    """Only for simple persistent list models."""

    def __init__(self, parent=None):
        super(CheckableProxyModel, self).__init__(parent)
        self._checked = set()

    def flags(self, index):
        if not index.isValid():
            return

        return super(CheckableProxyModel, self).flags(index) | Qt.ItemIsUserCheckable

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            return index.row()

        return super(CheckableProxyModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            if not value and index.row() in self._checked:
                self._checked.remove(index.row())
                return True
            elif value and index.row() not in self._checked:
                self._checked.add(index.row())
                return True

        return super(CheckableProxyModel, self).setData(index, role)

    def __getattr__(self, attr_name):
        return self.sourceModel().__getattribute__(attr_name)
