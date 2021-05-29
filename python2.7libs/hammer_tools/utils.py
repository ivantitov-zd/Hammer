from __future__ import print_function

import os
import subprocess
import sys

try:
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtGui import QKeySequence
except ImportError:
    from PySide2.QtWidgets import QAction
    from PySide2.QtGui import QKeySequence

import hou

from .settings import SettingsManager

settings = SettingsManager.instance()

isWindowsOS = sys.platform.startswith('win')
isLinuxOS = sys.platform.startswith('linux')
isMacOS = sys.platform == 'darwin'


def createAction(parent, label, callback=None, tip=None, icon=None, shortcut=None):
    action = QAction(label, parent)
    if callback is not None:
        action.triggered.connect(callback)
    if tip is not None:
        action.setToolTip(tip)
    if icon is not None:
        action.setIcon(icon)
    if shortcut is not None:
        action.setShortcut(QKeySequence(shortcut))
    return action


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().setParent(None)


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


def openLocation(path, select=False):
    new_path = os.path.normpath(path)
    path = None
    if not select and os.path.isfile(new_path):
        new_path = os.path.dirname(new_path)
    while not os.path.exists(new_path) and path != new_path:
        path = new_path
        new_path = os.path.dirname(path)
    if os.path.exists(new_path):
        if settings.value('hammer.open_location.use_custom_explorer') and \
                settings.value('hammer.open_location.custom_explorer_path'):
            exe = hou.expandString(settings.value('hammer.open_location.custom_explorer_path'))
            subprocess.call('{} "{}"'.format(exe, new_path))
        elif select:
            subprocess.call('explorer /select,"{0}"'.format(new_path.replace('/', '\\')))
        else:
            os.startfile(new_path)
