try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import FavoriteRole, InternalDataRole
from ..material import Material
from ..texture import TextureMap
from ..fuzzy import fuzzyMatch, fuzzyMatchWeight


class MaterialLibraryListProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(MaterialLibraryListProxyModel, self).__init__()

        self._favorite_only = False
        self._show_materials = True
        self._show_textures = True
        self._filter_pattern = None

    def onlyFavoriteShown(self):
        return self._favorite_only

    def showFavoriteOnly(self, show=True):
        self._favorite_only = show
        self.invalidateFilter()

    def areMaterialsShown(self):
        return self._show_materials

    def showMaterials(self, show=True):
        self._show_materials = show
        self.invalidateFilter()

    def areTexturesShown(self):
        return self._show_textures

    def showTextures(self, show=True):
        self._show_textures = show
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

        item = current_index.data(InternalDataRole)
        if isinstance(item, Material) and not self._show_materials:
            return False

        if isinstance(item, TextureMap) and not self._show_textures:
            return False

        if not self._filter_pattern:
            return True

        return fuzzyMatch(self._filter_pattern, current_index.data(Qt.DisplayRole).lower())

    def lessThan(self, source_left, source_right):
        if not self._filter_pattern:
            return source_left.row() > source_right.row()

        text1 = source_left.data(Qt.DisplayRole)
        text2 = source_right.data(Qt.DisplayRole)

        weight1 = fuzzyMatchWeight(self._filter_pattern, text1.lower())
        weight2 = fuzzyMatchWeight(self._filter_pattern, text2.lower())

        return weight1 < weight2

    def __getattr__(self, attr_name):
        return self.sourceModel().__getattribute__(attr_name)
