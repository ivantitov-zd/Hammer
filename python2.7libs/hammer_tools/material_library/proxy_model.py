try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from .library_browser.model import FavoriteRole


class MaterialLibraryListProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(MaterialLibraryListProxyModel, self).__init__()

        self._favorite_only = False
        self._filter_pattern = None

    def onlyFavoriteShown(self):
        return self._favorite_only

    def showFavoriteOnly(self, show=True):
        self._favorite_only = show
        self.invalidateFilter()

    def filterPattern(self):
        return self._filter_pattern

    def setFilterPattern(self, pattern):
        self._filter_pattern = pattern.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        current_index = self.sourceModel().index(source_row, 0, source_parent)

        if self._favorite_only and not current_index.data(FavoriteRole):
            return False

        if not self._filter_pattern:
            return True

        return self._filter_pattern in current_index.data(Qt.DisplayRole).lower()

    def __getattr__(self, attr_name):
        return self.sourceModel().__getattribute__(attr_name)
