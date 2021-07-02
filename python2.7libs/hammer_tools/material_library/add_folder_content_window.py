try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..widgets import LocationField, ComboBox, InputField
from . import ui
from .library_options_widget import LibraryOptionsWidget
from .library import Library
from .text import MONOSPACE_FONT


class Target:
    NoLibrary = 0
    NewLibrary = 1
    ExistingLibrary = 2


class AddFolderContentDialog(QDialog):
    def __init__(self, parent=None):
        super(AddFolderContentDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('Add folder content')
        self.setWindowIcon(ui.icon('SHELF_find_material', 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self._tabs = QTabWidget()
        main_layout.addWidget(self._tabs)

        main_tab_widget = QWidget()
        self._tabs.addTab(main_tab_widget, 'Main')

        main_tab_layout = QGridLayout(main_tab_widget)
        main_tab_layout.setContentsMargins(4, 4, 4, 4)
        main_tab_layout.setSpacing(4)

        self._path_label = QLabel('Path')
        main_tab_layout.addWidget(self._path_label, 0, 0)

        self._path_field = LocationField()
        main_tab_layout.addWidget(self._path_field, 0, 1)

        self._add_to_label = QLabel('Add to')
        main_tab_layout.addWidget(self._add_to_label, 1, 0)

        self._add_to_combo = ComboBox()
        self._add_to_combo.addItem('no library')
        self._add_to_combo.addItem('new library', Target.NewLibrary)
        self._add_to_combo.addItem('existing library', Target.ExistingLibrary)
        main_tab_layout.addWidget(self._add_to_combo, 1, 1)

        self._new_library_group = QGroupBox('Library')
        self._new_library_group.setHidden(True)
        self._add_to_combo.currentIndexChanged.connect(
            lambda i: self._new_library_group.setHidden(
                self._add_to_combo.itemData(i, Qt.UserRole) != Target.NewLibrary
            )
        )
        new_library_layout = QVBoxLayout(self._new_library_group)
        self._new_library_options_widget = LibraryOptionsWidget()
        new_library_layout.addWidget(self._new_library_options_widget)
        main_tab_layout.addWidget(self._new_library_group, 2, 0, 1, -1)

        self._existing_library_label = QLabel('Library')
        self._existing_library_label.setHidden(True)
        self._add_to_combo.currentIndexChanged.connect(
            lambda i: self._existing_library_label.setHidden(
                self._add_to_combo.itemData(i, Qt.UserRole) != Target.ExistingLibrary
            )
        )
        main_tab_layout.addWidget(self._existing_library_label, 3, 0)

        self._existing_library_combo = ComboBox()
        for library in Library.allLibraries():
            self._existing_library_combo.addItem(library.name(), library)
        self._existing_library_combo.setHidden(True)
        self._add_to_combo.currentIndexChanged.connect(
            lambda i: self._existing_library_combo.setHidden(
                self._add_to_combo.itemData(i, Qt.UserRole) != Target.ExistingLibrary
            )
        )
        main_tab_layout.addWidget(self._existing_library_combo, 3, 1)

        main_tab_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding), 4, 0, 1, -1)

        materials_tab_widget = QWidget()
        self._tabs.addTab(materials_tab_widget, 'Materials')

        materials_tab_layout = QGridLayout(materials_tab_widget)
        materials_tab_layout.setContentsMargins(4, 4, 4, 4)
        materials_tab_layout.setSpacing(4)

        self._add_materials_toggle = QCheckBox('Add materials')
        self._add_materials_toggle.setCheckable(True)
        self._add_materials_toggle.setChecked(True)
        materials_tab_layout.addWidget(self._add_materials_toggle, 0, 0, 1, -1)

        self._material_name_source_label = QLabel('Material name source')
        # materials_tab_layout.addWidget(self._material_name_source_label, 0, 0)

        self._material_name_source = ComboBox()
        self._material_name_source.addItems(['Folder name', 'Common part of texture names'])
        self._add_materials_toggle.toggled.connect(self._material_name_source.setEnabled)
        # materials_tab_layout.addWidget(self._material_name_source, 0, 1)

        self._material_favorite_toggle = QCheckBox('Mark as favorite')
        self._add_materials_toggle.toggled.connect(self._material_favorite_toggle.setEnabled)
        materials_tab_layout.addWidget(self._material_favorite_toggle, 2, 0, 1, -1)

        self._generate_material_thumbnails_toggle = QCheckBox('Generate thumbnails')
        self._generate_material_thumbnails_toggle.setChecked(True)
        self._add_materials_toggle.toggled.connect(self._generate_material_thumbnails_toggle.setEnabled)
        materials_tab_layout.addWidget(self._generate_material_thumbnails_toggle, 3, 0, 1, -1)

        materials_tab_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding), 4, 0, 1, -1)

        textures_tab_widget = QWidget()
        self._tabs.addTab(textures_tab_widget, 'Textures')

        textures_tab_layout = QGridLayout(textures_tab_widget)
        textures_tab_layout.setContentsMargins(4, 4, 4, 4)
        textures_tab_layout.setSpacing(4)

        self._add_textures_toggle = QCheckBox('Add textures')
        self._add_textures_toggle.setCheckable(True)
        self._add_textures_toggle.setChecked(True)
        textures_tab_layout.addWidget(self._add_textures_toggle, 0, 0, 1, -1)

        self._texture_favorite_toggle = QCheckBox('Mark as favorite')
        self._add_textures_toggle.toggled.connect(self._texture_favorite_toggle.setEnabled)
        textures_tab_layout.addWidget(self._texture_favorite_toggle, 1, 0, 1, -1)

        self._generate_texture_thumbnails_toggle = QCheckBox('Generate thumbnails')
        self._generate_texture_thumbnails_toggle.setChecked(True)
        self._add_textures_toggle.toggled.connect(self._generate_texture_thumbnails_toggle.setEnabled)
        textures_tab_layout.addWidget(self._generate_texture_thumbnails_toggle, 2, 0, 1, -1)

        textures_tab_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding), 3, 0, 1, -1)

        naming_tab_widget = QWidget()
        self._tabs.addTab(naming_tab_widget, 'Naming')

        naming_tab_layout = QGridLayout(naming_tab_widget)
        naming_tab_layout.setContentsMargins(4, 4, 4, 4)
        naming_tab_layout.setSpacing(4)

        self._remove_prefix_label = QLabel('Remove prefix')
        naming_tab_layout.addWidget(self._remove_prefix_label, 0, 0)

        self._remove_prefix_field = InputField()
        naming_tab_layout.addWidget(self._remove_prefix_field, 0, 1)

        self._remove_suffix_label = QLabel('Remove suffix')
        naming_tab_layout.addWidget(self._remove_suffix_label, 1, 0)

        self._remove_suffix_field = InputField()
        naming_tab_layout.addWidget(self._remove_suffix_field, 1, 1)

        self._remove_chars_label = QLabel('Replace chars with spaces')
        naming_tab_layout.addWidget(self._remove_chars_label, 2, 0)

        self._chars_to_replace_with_spaces_field = InputField('*')
        self._chars_to_replace_with_spaces_field.setFont(MONOSPACE_FONT)
        naming_tab_layout.addWidget(self._chars_to_replace_with_spaces_field, 2, 1)

        self._remove_repeated_spaces_toggle = QCheckBox('Remove repeated spaces')
        self._remove_repeated_spaces_toggle.setChecked(True)
        naming_tab_layout.addWidget(self._remove_repeated_spaces_toggle, 3, 0, 1, -1)

        self._switch_case_toggle = QCheckBox('Switch case to')
        self._switch_case_toggle.setChecked(True)
        naming_tab_layout.addWidget(self._switch_case_toggle, 4, 0)

        self._new_case_combo = QComboBox()
        self._switch_case_toggle.toggled.connect(self._new_case_combo.setEnabled)
        self._new_case_combo.addItems(['Title Case', 'Sentence case', 'lower case', 'UPPER CASE'])
        naming_tab_layout.addWidget(self._new_case_combo, 4, 1)

        self._keep_words_in_all_caps_toggle = QCheckBox('Keep words in all caps')
        self._keep_words_in_all_caps_toggle.setChecked(True)
        self._switch_case_toggle.toggled.connect(self._keep_words_in_all_caps_toggle.setEnabled)
        naming_tab_layout.addWidget(self._keep_words_in_all_caps_toggle, 5, 0, 1, -1)

        naming_tab_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding), 6, 0, 1, -1)

        main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding))

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
            'add_to': self._add_to_combo.currentData(),
            'existing_library': self._existing_library_combo.currentData(),
            'new_library_options': self._new_library_options_widget.options(),
            'naming_options': {
                'remove_prefix': self._remove_prefix_field.text(),
                'remove_suffix': self._remove_suffix_field.text(),
                'chars_to_replace_with_spaces': self._chars_to_replace_with_spaces_field.text(),
                'remove_repeated_spaces': self._remove_repeated_spaces_toggle.isChecked(),
                'switch_case': self._switch_case_toggle.isChecked(),
                'new_case': self._new_case_combo.currentIndex(),
                'keep_words_in_all_caps': self._keep_words_in_all_caps_toggle.isChecked()
            },
            'add_materials': self._add_materials_toggle.isChecked(),
            'mark_materials_as_favorite': self._material_favorite_toggle.isChecked(),
            'material_thumbnails': self._generate_material_thumbnails_toggle.isChecked(),
            'add_textures': self._add_textures_toggle.isChecked(),
            'mark_textures_as_favorite': self._texture_favorite_toggle.isChecked(),
            'texture_thumbnails': self._generate_texture_thumbnails_toggle.isChecked()
        }

    def setOptions(self, data):
        raise NotImplementedError
