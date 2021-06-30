try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from . import ui

FILTER_ICON = ui.icon('BUTTONS_filter', 16)
MATERIAL_ICON = ui.icon('SOP_material', 16)
TEXTURE_ICON = ui.icon('BUTTONS_parmmenu_texture', 16)


class FiltersWidget(QWidget):
    def __init__(self, parent=None):
        super(FiltersWidget, self).__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.show_materials_toggle = QPushButton()
        self.show_materials_toggle.setFixedWidth(24)
        self.show_materials_toggle.setCheckable(True)
        self.show_materials_toggle.setChecked(True)
        self.show_materials_toggle.setToolTip('Show materials')
        self.show_materials_toggle.setIcon(MATERIAL_ICON)
        layout.addWidget(self.show_materials_toggle)

        self.show_textures_toggle = QPushButton()
        self.show_textures_toggle.setFixedWidth(24)
        self.show_textures_toggle.setCheckable(True)
        self.show_textures_toggle.setChecked(True)
        self.show_textures_toggle.setToolTip('Show textures')
        self.show_textures_toggle.setIcon(TEXTURE_ICON)
        layout.addWidget(self.show_textures_toggle)


class FilterButton(QPushButton):
    def __init__(self):
        super(FilterButton, self).__init__()

        self.setFixedWidth(24)
        self.setToolTip('Filters')
        self.setIcon(FILTER_ICON)

        self._filters_popup = FiltersWidget(self)
        self.clicked.connect(self.showFilters)

    def showFilters(self):
        bottom = self.parent().mapToGlobal(self.geometry().bottomRight()).y()
        h_center = self.parent().mapToGlobal(self.geometry().center()).x()
        size = self._filters_popup.sizeHint()
        self._filters_popup.move(int(h_center - size.width() / 2), bottom)
        self._filters_popup.show()

    def popupWidget(self):
        return self._filters_popup
