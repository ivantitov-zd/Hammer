from __future__ import print_function

import json

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


def allSceneItems(root):
    return root.allSubChildren(recurse_in_locked_nodes=True)


class ExploreSceneDialog(QDialog):
    def __init__(self, parent=None):
        super(ExploreSceneDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Hammer: Explore Scene Alpha')
        self.setStyleSheet(hou.qt.styleSheet())
        self.resize(300, 200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.activate_button = QPushButton('Activate Explore Mode')
        self.activate_button.clicked.connect(lambda: self.activateExploreMode(True))
        main_layout.addWidget(self.activate_button)

        self.reset_button = QPushButton('Reset Original Scene State')
        self.reset_button.setDisabled(True)
        self.reset_button.clicked.connect(lambda: self.activateExploreMode(False))
        main_layout.addWidget(self.reset_button)

        self.show_all_comments_toggle = QCheckBox('Show All Comments')
        self.show_all_comments_toggle.setChecked(True)
        self.show_all_comments_toggle.setDisabled(True)
        self.show_all_comments_toggle.clicked.connect(self.applyCurrentSettings)
        main_layout.addWidget(self.show_all_comments_toggle)

        self.show_all_text_badges_toggle = QCheckBox('Show All Descriptions')
        self.show_all_text_badges_toggle.setChecked(True)
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
        for item in allSceneItems(hou.root()):
            if isinstance(item, hou.Node):
                if not item.parent().isEditable():
                    continue
                if 'hammer_explore' in item.userDataDict():
                    continue
                data = {}
                if item.isFlagWritable(hou.nodeFlag.Expose):
                    data['expose'] = item.isGenericFlagSet(hou.nodeFlag.Expose)
                if item.isFlagWritable(hou.nodeFlag.Display):
                    data['display'] = item.isGenericFlagSet(hou.nodeFlag.Display)
                if item.isFlagWritable(hou.nodeFlag.Template):
                    data['template'] = item.isGenericFlagSet(hou.nodeFlag.Template)
                if item.isFlagWritable(hou.nodeFlag.DisplayComment):
                    data['display_comment'] = item.isGenericFlagSet(hou.nodeFlag.DisplayComment)
                if item.isFlagWritable(hou.nodeFlag.DisplayDescriptiveName):
                    data['display_descriptive_name'] = item.isGenericFlagSet(hou.nodeFlag.DisplayDescriptiveName)
                item.setUserData('hammer_explore', json.dumps(data))

    def restoreOriginalSettingsFromScene(self, remove_data=True):
        for item in allSceneItems(hou.root()):
            if isinstance(item, hou.Node):
                if 'hammer_explore' not in item.userDataDict():
                    continue
                data = json.loads(item.userData('hammer_explore'))
                if 'expose' in data:
                    item.setGenericFlag(hou.nodeFlag.Expose, data.get('expose'))
                if data.get('display'):
                    item.setGenericFlag(hou.nodeFlag.Display, True)
                if 'template' in data:
                    item.setGenericFlag(hou.nodeFlag.Template, data.get('template'))
                if 'display_comment' in data:
                    item.setGenericFlag(hou.nodeFlag.DisplayComment, data.get('display_comment'))
                if 'display_descriptive_name' in data:
                    item.setGenericFlag(hou.nodeFlag.DisplayDescriptiveName, data.get('display_descriptive_name'))

                if remove_data:
                    item.destroyUserData('hammer_explore')

    def applyCurrentSettings(self):
        for item in allSceneItems(hou.root()):
            if isinstance(item, hou.Node):
                if item.isFlagWritable(hou.nodeFlag.DisplayComment):
                    item.setGenericFlag(hou.nodeFlag.DisplayComment, self.show_all_comments_toggle.isChecked())
            if item.isFlagWritable(hou.nodeFlag.DisplayDescriptiveName):
                item.setGenericFlag(hou.nodeFlag.DisplayDescriptiveName, self.show_all_text_badges_toggle.isChecked())

    def activateExploreMode(self, enable=True):
        if enable:
            self.saveOriginalSettingsToScene()
            self.applyCurrentSettings()
        else:
            self.restoreOriginalSettingsFromScene()
        self.activate_button.setDisabled(enable)
        self.reset_button.setEnabled(enable)
        self.show_all_comments_toggle.setEnabled(enable)
        self.show_all_text_badges_toggle.setEnabled(enable)
        self.hide_useless_nodes.setEnabled(enable)

    @classmethod
    def explore(cls):
        window = cls(hou.qt.mainWindow())
        window.show()
