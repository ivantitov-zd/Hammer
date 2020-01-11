from __future__ import print_function

import os
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


def fuzzyMatch(pattern, word):
    if pattern == word:
        return True, 999999
    weight = 0
    count = 0
    index = 0
    for char in word:
        try:
            if char == pattern[index]:
                count += 1
                index += 1
            elif count != 0:
                weight += count * count
                count = 0
        except IndexError:
            pass
    if count != 0:
        weight += count * count
    if index < len(pattern):
        return False, weight
    return True, weight


def openLocation(path):
    new_path = os.path.normpath(path)
    path = None
    if os.path.isfile(new_path):
        new_path = os.path.dirname(new_path)
    while not os.path.exists(new_path) and path != new_path:
        path = new_path
        new_path = os.path.dirname(path)
    if os.path.exists(new_path):
        os.startfile(new_path)
