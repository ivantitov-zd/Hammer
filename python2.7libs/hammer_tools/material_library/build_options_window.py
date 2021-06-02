try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class BuildOptionsWindow(QDialog):
    def __init__(self, widget, parent=None):
        super(BuildOptionsWindow, self).__init__(parent)

        self.setWindowTitle('Hammer: Material build options')
        self.setWindowIcon(hou.qt.Icon('SHELF_preflight', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._widget = widget
        layout.addWidget(widget)

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

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_button)

        self._ok_button = QPushButton('OK')
        self._ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self._ok_button)

    def options(self):
        return self._widget.options()

    def setOptions(self, options):
        self._widget.setOptions(options)
