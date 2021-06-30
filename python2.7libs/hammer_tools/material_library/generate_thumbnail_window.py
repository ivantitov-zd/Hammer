try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QDialog, QListWidget, QListWidgetItem, QTabWidget)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QDialog, QListWidget, QListWidgetItem, QTabWidget)
    from PySide2.QtCore import Qt

from . import ui
from .engine_connector import EngineConnector
from .preview_scenel_options_widget import PreviewSceneOptionsWidget


class GenerateThumbnailWindow(QDialog):
    def __init__(self, material=None, parent=None):
        super(GenerateThumbnailWindow, self).__init__(parent)

        self._material = material

        self.setWindowTitle('Generate thumbnail')
        self.setWindowIcon(ui.icon('NODEFLAGS_render', 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._engine_list = QListWidget()
        font = self._engine_list.font()
        font.setPointSize(ui.scaled(12))
        self._engine_list.setFont(font)
        self._tabs.addTab(self._engine_list, 'Engines')

        for engine in EngineConnector.engines():
            if not engine.isAvailable() or not engine.canCreateThumbnail():
                continue

            item = QListWidgetItem(engine.icon(), engine.name())
            item.setData(Qt.UserRole, engine)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self._engine_list.addItem(item)

        self._preview_scene_options_widget = PreviewSceneOptionsWidget()
        self._preview_scene_options_widget.layout().setContentsMargins(4, 4, 4, 4)
        self._tabs.addTab(self._preview_scene_options_widget, 'Scene Options')

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)
        layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)

        self._generate_button = QPushButton('Generate')
        self._generate_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self._generate_button)

    def options(self):
        return {
            'engines': tuple(self._engine_list.item(i).data(Qt.UserRole) for i in range(self._engine_list.count())
                             if self._engine_list.item(i).checkState() == Qt.Checked),
            'scene': self._preview_scene_options_widget.options()
        }
