import os

import hou

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class ActionPanel(QWidget):
    def __init__(self, parent=None, flags=None):
        super(ActionPanel, self).__init__(parent, flags or Qt.Window)

        self.node = None

    def updateTitle(self):
        if self.node:
            self.setWindowTitle('Hammer Action: ' + self.node.path())
        else:
            self.setWindowTitle('Hammer Action')

    def activate(self):
        self.updateTitle()

    def deactivate(self):
        pass

    def setSourceNode(self, node):
        self.node = node
        self.updateTitle()


class ActionWindow(ActionPanel):
    def __init__(self, parent=None):
        super(ActionWindow, self).__init__(parent)

        self.resize(350, 400)
        self.updateTitle()

    @classmethod
    def showForNode(cls, node=hou.node('/obj/')):
        window = cls(hou.qt.mainWindow())
        window.setSourceNode(node)
        window.show()
