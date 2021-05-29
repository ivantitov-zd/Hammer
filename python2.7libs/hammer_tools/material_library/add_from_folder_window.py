try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou

from ..widgets import LocationField
from .library import Library
from .material import Material
from .thumbnail import updateMaterialThumbnails


class Target:
    NoLibrary = 0
    NewLibrary = 1
    ExistingLibrary = 2


class AddFromFolderDialog(QDialog):
    def __init__(self, parent=None):
        super(AddFromFolderDialog, self).__init__(parent)

        self.setWindowTitle('Hammer: Add from folder')
        self.setWindowIcon(hou.qt.Icon('SHELF_find_material', 32, 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self.path_field = LocationField()
        self.path_field.label.hide()
        form_layout.addRow('Scan path', self.path_field)

        self.target_library_mode = QComboBox()
        self.target_library_mode.addItem('No library')
        self.target_library_mode.addItem('New library', Target.NewLibrary)
        self.target_library_mode.addItem('Existing library', Target.ExistingLibrary)
        form_layout.addRow('Target', self.target_library_mode)

        self.library_name_field = QLineEdit()
        self.library_name_field.setDisabled(True)
        self.target_library_mode.currentIndexChanged.connect(
            lambda i: self.library_name_field.setDisabled(
                self.target_library_mode.itemData(i, Qt.UserRole) != Target.NewLibrary
            )
        )
        form_layout.addRow('Library name', self.library_name_field)

        self.existing_libraries_combo = QComboBox()
        for library in Library.allLibraries():
            self.existing_libraries_combo.addItem(library.name(), library)
        self.existing_libraries_combo.setDisabled(True)
        self.target_library_mode.currentIndexChanged.connect(
            lambda i: self.existing_libraries_combo.setDisabled(
                self.target_library_mode.itemData(i, Qt.UserRole) != Target.ExistingLibrary
            )
        )
        form_layout.addRow('Library', self.existing_libraries_combo)

        # self.material_name_source = QComboBox()
        # self.material_name_source.addItems(['Folder name', 'Common part of texture names'])
        # form_layout.addRow('Material name source', self.material_name_source)

        self.favorite_toggle = QCheckBox('Favorite')
        form_layout.addWidget(self.favorite_toggle)

        self.generate_thumbnails_toggle = QCheckBox('Generate thumbnails')
        form_layout.addWidget(self.generate_thumbnails_toggle)

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

        self.add_library_button = QPushButton('Add')
        self.add_library_button.clicked.connect(self.accept)
        button_layout.addWidget(self.add_library_button)
