try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class InputField(QLineEdit):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Cancel):
            self.clear()
        else:
            super(InputField, self).keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
            self.clear()
        else:
            super(InputField, self).mouseReleaseEvent(event)
