try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from .field_base import FieldBase


class InputField(FieldBase):
    def __init__(self, text=None, label_text=None, label_width=None):
        super(InputField, self).__init__(label_text, label_width)

        self.text_field = QLineEdit()
        if text:
            self.text_field.setText(text)
        self.layout().addWidget(self.text_field)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Cancel):
            self.clear()
        else:
            super(InputField, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
            self.clear()
        else:
            super(InputField, self).mousePressEvent(event)

    def __getattr__(self, attr_name):
        return self.text_field.__getattribute__(attr_name)
