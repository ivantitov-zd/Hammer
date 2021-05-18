try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QDialog)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QDialog)
    from PySide2.QtCore import Qt

import hou


class RemoveLibraryWindow(QDialog):
    def __init__(self, library=None):
        super(RemoveLibraryWindow, self).__init__()

        self._library = library

        self.updateWindowTitle()
        self.setWindowIcon(hou.qt.Icon('BUTTONS_material_exclude', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._remove_materials_toggle = QCheckBox('Remove bound materials')
        layout.addWidget(self._remove_materials_toggle)

        self._remove_bound_only_to_current_toggle = QCheckBox('Single-bound materials only')
        self._remove_bound_only_to_current_toggle.setDisabled(True)
        self._remove_bound_only_to_current_toggle.setChecked(True)
        self._remove_materials_toggle.toggled.connect(self._remove_bound_only_to_current_toggle.setEnabled)
        layout.addWidget(self._remove_bound_only_to_current_toggle)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        layout.addLayout(button_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        button_layout.addSpacerItem(spacer)

        self._add_library_button = QPushButton('Remove')
        self._add_library_button.clicked.connect(self.accept)
        button_layout.addWidget(self._add_library_button)

    def updateWindowTitle(self):
        title = 'Hammer: Remove material library'
        if self._library is not None:
            title += ' "{}"'.format(self._library.name())
        self.setWindowTitle(title)

    def removeMaterials(self):
        return self._remove_materials_toggle.isChecked()

    def onlySingleBoundMaterials(self):
        return self._remove_bound_only_to_current_toggle.isChecked()
