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


class ExploreSceneDialog(QDialog):
    def __init__(self, parent=None):
        super(ExploreSceneDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Hammer: Explore Scene Beta')
        self.setStyleSheet(hou.qt.styleSheet())
        self.resize(300, 200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.activate_button = QPushButton('Activate Explore Mode')
        self.activate_button.clicked.connect(self.activateExploreMode)
        main_layout.addWidget(self.activate_button)

        self.reset_button = QPushButton('Reset Original Scene State')
        self.reset_button.setDisabled(True)
        self.reset_button.clicked.connect(lambda: self.activateExploreMode(False))
        main_layout.addWidget(self.reset_button)

        self.show_all_notes_toggle = QCheckBox('Show All Notes')
        self.show_all_notes_toggle.setDisabled(True)
        self.show_all_notes_toggle.clicked.connect(self.applyCurrentSettings)
        main_layout.addWidget(self.show_all_notes_toggle)

        self.show_all_comments_toggle = QCheckBox('Show All Comments')
        self.show_all_comments_toggle.setDisabled(True)
        self.show_all_comments_toggle.clicked.connect(self.applyCurrentSettings)
        main_layout.addWidget(self.show_all_comments_toggle)

        self.show_all_text_badges_toggle = QCheckBox('Show All Text Badges')
        self.show_all_text_badges_toggle.setDisabled(True)
        self.show_all_text_badges_toggle.clicked.connect(self.applyCurrentSettings)
        main_layout.addWidget(self.show_all_text_badges_toggle)

        self.hide_useless_nodes = QCheckBox('Hide Useless Nodes')
        self.hide_useless_nodes.setDisabled(True)
        self.hide_useless_nodes.clicked.connect(self.applyCurrentSettings)
        main_layout.addWidget(self.hide_useless_nodes)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

    def saveOriginalSettingsToScene(self):
        pass

    def loadOriginalSettingsFromScene(self):
        pass

    def activateExploreMode(self, enable=True):
        if enable:
            self.saveOriginalSettingsToScene()
        self.activate_button.setDisabled(enable)
        self.reset_button.setEnabled(enable)
        self.show_all_notes_toggle.setEnabled(enable)
        self.show_all_comments_toggle.setEnabled(enable)
        self.show_all_text_badges_toggle.setEnabled(enable)
        self.hide_useless_nodes.setEnabled(enable)

    def applyCurrentSettings(self):
        pass

    @classmethod
    def explore(cls):
        window = cls(hou.qt.mainWindow())
        window.show()
