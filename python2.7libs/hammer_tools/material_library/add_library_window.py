try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou

from .library import Library


class AddLibraryDialog(QDialog):
    def __init__(self, parent=None):
        super(AddLibraryDialog, self).__init__(parent)

        self.setWindowTitle('Hammer: Add Material Library')
        self.setWindowIcon(hou.qt.Icon('LOP_materiallibrary', 32, 32))
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self.library_name_field = QLineEdit()
        form_layout.addRow('Library name', self.library_name_field)

        self.comment_edit = QTextEdit()
        self.comment_edit.setAutoFillBackground(False)
        form_layout.addRow('Comment', self.comment_edit)

        self.favorite_toggle = QCheckBox('Favorite')
        form_layout.addWidget(self.favorite_toggle)

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

    @staticmethod
    def addLibrary():
        window = AddLibraryDialog(hou.qt.mainWindow())
        r = window.exec_()
        if r:
            Library.addLibrary({
                'name': window.library_name_field.text(),
                'comment': window.comment_edit.toPlainText(),
                'favorite': window.favorite_toggle.isChecked()
            })
        return r
