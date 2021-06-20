try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class LibraryOptionsWidget(QWidget):
    def __init__(self):
        super(LibraryOptionsWidget, self).__init__()

        layout = QFormLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.name_field = QLineEdit()
        layout.addRow('Name', self.name_field)

        self.comment_field = QTextEdit()
        self.comment_field.setAutoFillBackground(False)
        layout.addRow('Comment', self.comment_field)

        self.favorite_toggle = QCheckBox('Favorite')
        layout.addWidget(self.favorite_toggle)

    def options(self):
        return {
            'name': self.name_field.text() or None,
            'comment': self.comment_field.toPlainText() or None,
            'favorite': self.favorite_toggle.isChecked()
        }

    def setOptions(self, data):
        self.name_field.setText(data.get('name', ''))
        self.comment_field.setPlainText(data.get('comment', ''))
        self.favorite_toggle.setChecked(data.get('favorite', False))
