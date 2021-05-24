try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


def isRevertToDefaultEvent(event):
    return event.modifiers() == Qt.ControlModifier and event.button() == Qt.MiddleButton


class Slider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(Slider, self).__init__(orientation, parent)
        self._default_value = 0
        self._value_ladder_active = False

    def revertToDefault(self):
        self.setValue(self._default_value)

    def setDefaultValue(self, value):
        self._default_value = value

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:  # Todo: Revert to default
            hou.ui.openValueLadder(self.value(), self.setValue,
                                   data_type=hou.valueLadderDataType.Int)
            self._value_ladder_active = True
        elif event.button() == Qt.LeftButton:
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier)
        super(Slider, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._value_ladder_active:
            hou.ui.updateValueLadder(event.globalX(), event.globalY(),
                                     bool(event.modifiers() & Qt.AltModifier),
                                     bool(event.modifiers() & Qt.ShiftModifier))
        else:
            super(Slider, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._value_ladder_active and event.button() == Qt.MiddleButton:
            hou.ui.closeValueLadder()
            self._value_ladder_active = False
        elif isRevertToDefaultEvent(event):
            self.revertToDefault()
        else:
            super(Slider, self).mouseReleaseEvent(event)
