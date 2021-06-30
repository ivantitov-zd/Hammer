try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class TextureOptionsWidget(QWidget):
    def __init__(self):
        super(TextureOptionsWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.name_label = QLabel('Name')
        layout.addWidget(self.name_label, 0, 0)

        self.name_field = QLineEdit()
        layout.addWidget(self.name_field, 0, 1)

        self.comment_label = QLabel('Comment')
        layout.addWidget(self.comment_label, 1, 0, Qt.AlignLeft | Qt.AlignTop)

        self.comment_field = QTextEdit()
        layout.addWidget(self.comment_field, 1, 1)

        self.favorite_toggle = QCheckBox('Mark as favorite')
        layout.addWidget(self.favorite_toggle, 2, 0, 1, -1)

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
