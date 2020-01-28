from __future__ import print_function

import os

import hou

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


from .quick_selection import FilterField


class ParmPresetModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ParmPresetModel, self).__init__(parent)


class SplineDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(SplineDelegate, self).__init__(parent)


class ParmPresetView(QListView):
    # Signals
    accepted = Signal()

    def __init__(self):
        super(ParmPresetView, self).__init__()

        self.setFrameStyle(self.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit()
        else:
            super(SelectListView, self).keyPressEvent(event)


class ParmPresetDialog(QDialog):
    def __init__(self, parent=None):
        super(ParmPresetDialog, self).__init__(parent, Qt.Window)

        self.setStyleSheet(hou.qt.styleSheet())

        # Filter
        self.filter_field = FilterField()

        # List
        self.list_view = ParmPresetView()

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        main_layout.addWidget(self.filter_field)
        main_layout.addWidget(self.list_view)

        pass


class SuperFormulaPresetDialog(ParmPresetDialog):
    def __init__(self, parent=None):
        super(SuperFormulaPresetDialog, self).__init__(parent)

        self.setWindowTitle('Super Formula Presets')

        # Model
        self.model = None
