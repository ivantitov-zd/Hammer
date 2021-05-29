try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QDialog, QListWidget, QListWidgetItem)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QDialog, QListWidget, QListWidgetItem)
    from PySide2.QtCore import Qt

import hou

# from ...widgets import FilePathField
from ..engine_connector import EngineConnector


class GenerateThumbnailWindow(QDialog):
    def __init__(self, material=None):
        super(GenerateThumbnailWindow, self).__init__()

        self._material = material

        self.setWindowTitle('Hammer: Generate thumbnail')
        self.setWindowIcon(hou.qt.Icon('NODEFLAGS_render', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._generate_default_thumbnail_toggle = QCheckBox('Generate default thumbnail (OpenGL)')
        layout.addWidget(self._generate_default_thumbnail_toggle)

        self._generate_thumbnails_for_engines_toggle = QCheckBox('Generate thumbnails for engines')
        layout.addWidget(self._generate_thumbnails_for_engines_toggle)

        self._engine_list = QListWidget()
        for engine in EngineConnector.engines():
            item = QListWidgetItem(engine.icon(), engine.name())
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            item.setData(Qt.UserRole, engine)
            self._engine_list.addItem(item)

        # self._use_custom_geometry_toggle = QCheckBox('Use custom geometry')
        # layout.addWidget(self._use_custom_geometry_toggle)
        #
        # self._custom_geometry_path_field = QLineEdit()
        # layout.addWidget(self._custom_geometry_path_field)

        # self._use_custom_hdri_toggle = QCheckBox('Use custom HDRI')
        # layout.addWidget(self._use_custom_hdri_toggle)
        #
        # self._custom_hdri_path_field = FilePathField('$JOB', 'HDRI (*.hdr *.exr *.rat); All (*.*)')
        # layout.addWidget(self._custom_hdri_path_field)

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

        self._add_library_button = QPushButton('Generate')
        self._add_library_button.clicked.connect(self.accept)
        button_layout.addWidget(self._add_library_button)

    def generateDefault(self):
        return self._generate_default_thumbnail_toggle.isChecked()

    def generateForEngines(self):
        return self._generate_thumbnails_for_engines_toggle.isChecked()

    # def useCustomGeometry(self):
    #     return self._use_custom_geometry_toggle.isChecked()

    # def customGeometry(self):
    #     return self._custom_geometry_path_field

    # def useCustomHDRI(self):
    #     return self._use_custom_hdri_toggle.isChecked()

    # def customHDRIPath(self):
    #     return self._custom_hdri_path_field
