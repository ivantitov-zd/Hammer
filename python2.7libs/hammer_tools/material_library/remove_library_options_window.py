try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QDialog)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QDialog)
    from PySide2.QtCore import Qt

import hou


class RemoveLibraryOptionsWindow(QDialog):
    def __init__(self, libraries=None, parent=None):
        super(RemoveLibraryOptionsWindow, self).__init__(parent)

        self._libraries = libraries

        self.setWindowTitle('Hammer: Remove material library')
        self.setWindowIcon(hou.qt.Icon('BUTTONS_material_exclude', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._materials_toggle = QCheckBox('Remove bound materials')
        layout.addWidget(self._materials_toggle)

        self._materials_bound_only_to_current_toggle = QCheckBox('Single-bound materials only')
        self._materials_bound_only_to_current_toggle.setDisabled(True)
        self._materials_bound_only_to_current_toggle.setChecked(True)
        self._materials_toggle.toggled.connect(self._materials_bound_only_to_current_toggle.setEnabled)
        layout.addWidget(self._materials_bound_only_to_current_toggle)

        self._textures_toggle = QCheckBox('Remove bound textures')
        layout.addWidget(self._textures_toggle)

        self._textures_bound_only_to_current_toggle = QCheckBox('Single-bound textures only')
        self._textures_bound_only_to_current_toggle.setDisabled(True)
        self._textures_bound_only_to_current_toggle.setChecked(True)
        self._textures_toggle.toggled.connect(self._textures_bound_only_to_current_toggle.setEnabled)
        layout.addWidget(self._textures_bound_only_to_current_toggle)

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

        self._remove_button = QPushButton('Remove')
        self._remove_button.clicked.connect(self.accept)
        button_layout.addWidget(self._remove_button)

    def options(self):
        return {
            'remove_materials': self._materials_toggle.isChecked(),
            'only_single_bound_materials': self._materials_bound_only_to_current_toggle.isChecked(),
            'remove_textures': self._textures_toggle.isChecked(),
            'only_single_bound_textures': self._textures_bound_only_to_current_toggle.isChecked()
        }

    def setOptions(self, data):
        raise NotImplementedError
