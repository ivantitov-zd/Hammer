try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from . import ui
from .texture_options_widget import TextureOptionsWidget
from .library_bindings_widget import LibraryBindingsWidget


class EditTextureWindow(QDialog):
    def __init__(self, parent=None):
        super(EditTextureWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('Edit library')
        self.setWindowIcon(ui.icon('LOP_editmaterial', 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self._tabs = QTabWidget()
        main_layout.addWidget(self._tabs)

        self._texture_options_widget = TextureOptionsWidget()
        self._texture_options_widget.layout().setContentsMargins(4, 4, 4, 4)
        self._tabs.addTab(self._texture_options_widget, 'Main')

        self._library_bindings = LibraryBindingsWidget()
        self._tabs.addTab(self._library_bindings, 'Library bindings')

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

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

    def options(self):
        return {
            'main': self._texture_options_widget.options(),
            'library_bindings': self._library_bindings  # Todo
        }

    def setOptions(self, texture):
        self._texture_options_widget.setOptions(texture.asData())
