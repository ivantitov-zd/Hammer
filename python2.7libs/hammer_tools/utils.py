from __future__ import print_function

import sys

try:
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtGui import QKeySequence
except ImportError:
    from PySide2.QtWidgets import QAction
    from PySide2.QtGui import QKeySequence


isWindowsOS = sys.platform.startswith('win')
isLinuxOS = sys.platform.startswith('linux')
isMacOS = sys.platform == 'darwin'


def createAction(parent, label, callback=None, help=None, icon=None, shortcut=None):
    action = QAction(label, parent)
    if callback is not None:
        action.triggered.connect(callback)
    if help is not None:
        action.setToolTip(help)
    if icon is not None:
        action.setIcon(icon)
    if shortcut is not None:
        action.setShortcut(QKeySequence(shortcut))
    return action
