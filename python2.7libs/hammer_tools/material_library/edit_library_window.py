try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from . import ui
from .library_options_widget import LibraryOptionsWidget


class EditLibraryWindow(QDialog):
    def __init__(self, parent=None):
        super(EditLibraryWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('Edit library')
        self.setWindowIcon(ui.icon('LOP_editmaterial', 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self._tabs = QTabWidget()
        main_layout.addWidget(self._tabs)

        self._library_options_widget = LibraryOptionsWidget()
        self._library_options_widget.layout().setContentsMargins(4, 4, 4, 4)
        self._tabs.addTab(self._library_options_widget, 'Main')

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
            'main': self._library_options_widget.options()
        }

    def setOptions(self, library):
        self._library_options_widget.setOptions(library.asData())
