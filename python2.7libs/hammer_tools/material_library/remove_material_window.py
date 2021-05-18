try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QApplication)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QApplication)
    from PySide2.QtCore import Qt

import hou


class RemoveMaterialWindow(QWidget):
    def __init__(self, library=None):
        super(RemoveMaterialWindow, self).__init__()

        self.library = library

        self.updateWindowTitle()
        self.setWindowIcon(hou.qt.Icon('BUTTONS_material_exclude', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.remove_only_from_this_library_toggle = QCheckBox('Remove only from this library')
        layout.addWidget(self.remove_only_from_this_library_toggle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        layout.addLayout(button_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        button_layout.addSpacerItem(spacer)

        self.add_library_button = QPushButton('Remove')
        self.add_library_button.clicked.connect(self.accept)
        button_layout.addWidget(self.add_library_button)

    def updateWindowTitle(self):
        title = 'Hammer: Remove material'
        if self.library is not None:
            title += ' {}'.format(self.library.name())
        self.setWindowTitle(title)
