from __future__ import print_function

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import QIcon, QKeySequence
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import QIcon, QKeySequence

from .. import ui
from ..data_roles import InternalDataRole
from .map_types_view import MapTypesView
from .map_types_model import MapTypesModel
from .labels_view import LabelsView
from .labels_model import LabelsModel
from ..map_type import MapType

LIST_ADD_ICON = ui.icon('BUTTONS_list_add', 16)
LIST_DELETE_ICON = ui.icon('BUTTONS_list_delete', 16)
CANCEL_CHANGES_ICON = ui.icon('BUTTONS_close', 16)


class LabelsEditorWindow(QDialog):
    def __init__(self, parent=None):
        super(LabelsEditorWindow, self).__init__(parent)

        self.changes = {
            map_type: {'labels': MapType.labels(map_type, reload=True),
                       'delete': [],
                       'new': [],
                       'renaming': {}}
            for map_type in MapType.allTypes()
        }

        self.setWindowTitle('Labels editor')
        self.setWindowIcon(ui.icon('LOP_editproperties', 32))
        self.resize(500, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self._splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self._splitter)

        self._map_types_model = MapTypesModel(self)

        self._map_types_view = MapTypesView()
        self._map_types_view.setModel(self._map_types_model)
        self._splitter.addWidget(self._map_types_view)

        labels_area_widget = QWidget()
        self._splitter.addWidget(labels_area_widget)

        labels_area_layout = QVBoxLayout(labels_area_widget)
        labels_area_layout.setContentsMargins(0, 0, 0, 0)
        labels_area_layout.setSpacing(4)

        self._toolbar = QToolBar()
        labels_area_layout.addWidget(self._toolbar)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self._toolbar.addWidget(spacer)

        self._add_label_action = QAction(LIST_ADD_ICON, 'Add', self)
        self._add_label_action.setShortcut(QKeySequence('+'))
        self._add_label_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._toolbar.addAction(self._add_label_action)

        self._remove_label_action = QAction(LIST_DELETE_ICON, 'Remove', self)
        self._remove_label_action.setShortcut(QKeySequence.Delete)
        self._remove_label_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._toolbar.addAction(self._remove_label_action)

        self._cancel_changes_action = QAction(CANCEL_CHANGES_ICON, 'Cancel changes', self)
        self._cancel_changes_action.setShortcut(QKeySequence.Delete)
        self._cancel_changes_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._toolbar.addAction(self._cancel_changes_action)

        self._labels_model = LabelsModel(self.changes, self)
        selection_model = self._map_types_view.selectionModel()
        selection_model.currentChanged.connect(
            lambda index: self._labels_model.setMapType(index.data(InternalDataRole))
        )
        self._add_label_action.triggered.connect(self._labels_model.addRow)
        self._cancel_changes_action.triggered.connect(self._labels_model.cancelChanges)

        self._labels_view = LabelsView()
        self._labels_view.setModel(self._labels_model)
        self._labels_view.addAction(self._add_label_action)
        self._remove_label_action.triggered.connect(
            lambda: self._labels_model.removeRow(self._labels_view.currentIndex().row())
        )
        labels_area_layout.addWidget(self._labels_view)

        self._splitter.setSizes([140, self._splitter.width() - 140])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self._ok_button = QPushButton('OK')
        self._ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self._ok_button)

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)
