from __future__ import print_function

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


def setRampParmInterpolation(parm, basis):
    """Sets interpolation for all knots."""
    try:
        source_ramp = parm.evalAsRamp()
        bases = (basis,) * len(source_ramp.basis())
        new_ramp = hou.Ramp(bases, source_ramp.keys(), source_ramp.values())
        parm.set(new_ramp)
    except hou.PermissionError:
        pass


def chooseFileAndSetParm(parm):
    if isinstance(parm, str):
        parm = hou.parm(parm)
    directory = os.path.dirname(parm.eval())
    exists = os.path.exists(directory)
    directory = directory.encode('utf-8') if exists else hou.expandString(u'$HIP/')
    template = parm.parmTemplate()
    is_directory = template.dataType() == hou.parmData.String and template.fileType() == hou.fileType.Directory
    title = (u'Folder' if is_directory else u'File') + u' for {}: {}'.format(parm.node().path(), parm.description())
    if is_directory:
        path = QFileDialog.getExistingDirectory(hou.qt.mainWindow(), caption=title, directory=directory)
    else:
        path = QFileDialog.getOpenFileName(hou.qt.mainWindow(), caption=title, dir=directory, filter=u'*.*')[0]
    if path:
        parm.set(path)
