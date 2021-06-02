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
        self.text_field.installEventFilter(self)
        if text:
            self.text_field.setText(text)
        self.layout().addWidget(self.text_field)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Cancel):
            self.text_field.clear()
        else:
            super(InputField, self).keyPressEvent(event)

    def eventFilter(self, watched, event):
        if watched == self.text_field:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
                    self.text_field.clear()
                    return True
        return False

    def __getattr__(self, attr_name):
        return self.text_field.__getattribute__(attr_name)
