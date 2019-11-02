from __future__ import print_function

import json
import os

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

PREF_FILE = hou.homeHoudiniDirectory() + '/hammer_tools.pref'


class HammerPreferencesDialog(QDialog):
    # Signals
    preferencesUpdated = Signal()

    def __init__(self):
        super(HammerPreferencesDialog, self).__init__()

        self.data = {'Previous Files': {'Value': True, 'Desc': ''},
                     'Open Folder': {'Value': True, 'Desc': ''},
                     'Select': {'Value': True, 'Desc': ''},
                     'Select Font': {'Value': True, 'Desc': ''},
                     'Set Interpolation': {'Value': True,'Desc': ''}}

        self.setWindowTitle('Hammer Tools: Preferences')
        self.setProperty('houdiniStyle', True)

    def updatePreferences(self):
        if not os.path.exists(PREF_FILE):
            return
        try:
            with open(PREF_FILE, 'r') as file:
                self.data.update(json.load(file))
        except:
            pass
        self.preferencesUpdated.emit()

    def savePreferences(self):
        try:
            with open(PREF_FILE, 'wt') as file:
                json.dump(self.data, file, ensure_ascii=True, indent=4)
        except IOError:
            pass
