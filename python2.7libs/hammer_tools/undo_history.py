from __future__ import print_function

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


class UndoHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super(UndoHistoryDialog, self).__init__(parent, Qt.Window)

        # Data
        self.__original = 0
        self.__previous = 0
        # self.__history = ()

        # UI
        self.setWindowTitle('Undo History (Beta)')
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.history_slider = QSlider(Qt.Horizontal)
        self.history_slider.valueChanged.connect(self.moveToMoment)
        main_layout.addWidget(self.history_slider)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset)
        main_layout.addWidget(self.reset_button)

    def moveToMoment(self, pos):
        if pos > self.__previous:
            for _ in range(pos - self.__previous):
                hou.undos.performRedo()
        else:
            for _ in range(self.__previous - pos):
                hou.undos.performUndo()
        self.__previous = pos

    def reset(self):
        self.moveToMoment(self.__original)
        self.history_slider.blockSignals(True)
        self.history_slider.setValue(self.__original)
        self.history_slider.blockSignals(False)

    def updateHistory(self):
        undo_list = hou.undos.undoLabels()
        redo_list = hou.undos.redoLabels()
        self.history_slider.setRange(0, len(undo_list) + len(redo_list))
        self.__original = len(undo_list)
        self.__previous = self.__original
        self.history_slider.setValue(self.__original)
        # self.__history = undo_list + ('Original',) + redo_list


def showUndoHistory():
    if not hasattr(hou.session, 'hammer_undo_history'):
        hou.session.hammer_undo_history = UndoHistoryDialog(hou.qt.mainWindow())
    hou.session.hammer_undo_history.updateHistory()
    hou.session.hammer_undo_history.show()
