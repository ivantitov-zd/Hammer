try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou

from .library_options_widget import LibraryOptionsWidget


class AddLibraryDialog(QDialog):
    def __init__(self, parent=None):
        super(AddLibraryDialog, self).__init__(parent)

        self.setWindowTitle('Hammer: Add Material Library')
        self.setWindowIcon(hou.qt.Icon('LOP_materiallibrary', 32, 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self._library_options_widget = LibraryOptionsWidget()
        self.options = self._library_options_widget.options
        self.setOptions = self._library_options_widget.setOptions
        main_layout.addWidget(self._library_options_widget)

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
