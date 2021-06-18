try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou

from ..widgets import LocationField, ComboBox
from .library import Library


class Target:
    NoLibrary = 0
    NewLibrary = 1
    ExistingLibrary = 2


class AddFolderContentDialog(QDialog):
    def __init__(self, parent=None):
        super(AddFolderContentDialog, self).__init__(parent)

        self.setWindowTitle('Hammer: Add folder content')
        self.setWindowIcon(hou.qt.Icon('SHELF_find_material', 32, 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self._path_field = LocationField()
        self._path_field.label.hide()
        form_layout.addRow('Scan path', self._path_field)

        self._target_library_mode = ComboBox()
        self._target_library_mode.addItem('No library')
        self._target_library_mode.addItem('New library', Target.NewLibrary)
        self._target_library_mode.addItem('Existing library', Target.ExistingLibrary)
        form_layout.addRow('Target', self._target_library_mode)

        self.library_name_field = QLineEdit()
        self.library_name_field.setDisabled(True)
        self._target_library_mode.currentIndexChanged.connect(
            lambda i: self.library_name_field.setDisabled(
                self._target_library_mode.itemData(i, Qt.UserRole) != Target.NewLibrary
            )
        )
        form_layout.addRow('Library name', self.library_name_field)

        self._existing_libraries_combo = ComboBox()
        for library in Library.allLibraries():
            self._existing_libraries_combo.addItem(library.name(), library)
        self._existing_libraries_combo.setDisabled(True)
        self._target_library_mode.currentIndexChanged.connect(
            lambda i: self._existing_libraries_combo.setDisabled(
                self._target_library_mode.itemData(i, Qt.UserRole) != Target.ExistingLibrary
            )
        )
        form_layout.addRow('Library', self._existing_libraries_combo)

        self._material_group_box = QGroupBox('Materials')
        self._material_group_box.setFlat(True)
        self._material_group_box.setCheckable(True)
        self._material_group_box.setChecked(True)
        main_layout.addWidget(self._material_group_box)

        material_group_layout = QGridLayout(self._material_group_box)
        material_group_layout.setContentsMargins(4, 4, 4, 4)
        material_group_layout.setSpacing(4)
        # Bug fix https://help.quixel.com/hc/en-us/community/posts/360011811537-Houdini-18-460-Missing-UI-TEMP-FIX
        self._material_group_box.setContentsMargins(10, 14, 10, 8)

        self._material_name_source_label = QLabel('Material name source')
        material_group_layout.addWidget(self._material_name_source_label, 0, 0)

        self._material_name_source = ComboBox()
        self._material_name_source.addItems(['Folder name', 'Common part of texture names'])
        material_group_layout.addWidget(self._material_name_source, 0, 1)

        self._material_favorite_toggle = QCheckBox('Mark as favorite')
        material_group_layout.addWidget(self._material_favorite_toggle, 1, 0)

        self._generate_material_thumbnails_toggle = QCheckBox('Generate thumbnails')
        material_group_layout.addWidget(self._generate_material_thumbnails_toggle, 2, 0)

        self._texture_group_box = QGroupBox('Textures')
        self._texture_group_box.setFlat(True)
        self._texture_group_box.setCheckable(True)
        self._texture_group_box.setChecked(True)
        main_layout.addWidget(self._texture_group_box)

        texture_group_layout = QGridLayout(self._texture_group_box)
        texture_group_layout.setContentsMargins(4, 4, 4, 4)
        texture_group_layout.setSpacing(4)
        # Bug fix https://help.quixel.com/hc/en-us/community/posts/360011811537-Houdini-18-460-Missing-UI-TEMP-FIX
        self._texture_group_box.setContentsMargins(10, 14, 10, 8)

        self._texture_name_source_label = QLabel('Texture name source')
        texture_group_layout.addWidget(self._texture_name_source_label, 0, 0)

        self.texture_name_source = ComboBox()
        self.texture_name_source.addItems(['Folder name', 'Common part of texture names'])
        texture_group_layout.addWidget(self.texture_name_source, 0, 1)

        self._texture_favorite_toggle = QCheckBox('Mark as favorite')
        texture_group_layout.addWidget(self._texture_favorite_toggle, 1, 0)

        self._generate_texture_thumbnails_toggle = QCheckBox('Generate thumbnails')
        texture_group_layout.addWidget(self._generate_texture_thumbnails_toggle, 2, 0)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        main_layout.addLayout(button_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        button_layout.addSpacerItem(spacer)

        self._scan_add_content_button = QPushButton('Scan and add')
        self._scan_add_content_button.clicked.connect(self.accept)
        button_layout.addWidget(self._scan_add_content_button)

    def options(self):
        return {
            'path': self._path_field.path(),
            'add_to': self._target_library_mode.currentData(),
            'existing_library': self._existing_libraries_combo.currentData(),
            'add_materials': self._material_group_box.isChecked(),
            'mark_materials_as_favorite': self._material_favorite_toggle.isChecked(),
            'material_thumbnails': self._generate_material_thumbnails_toggle.isChecked(),
            'add_textures': self._texture_group_box.isChecked(),
            'mark_textures_as_favorite': self._texture_favorite_toggle.isChecked(),
            'texture_thumbnails': self._generate_texture_thumbnails_toggle.isChecked()
        }

    def setOptions(self, data):
        raise NotImplementedError
