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

from .utils import openLocation


def setRampParmInterpolation(parm, basis):
    """Sets interpolation for all knots."""
    source_ramp = parm.evalAsRamp()
    bases = (basis,) * len(source_ramp.basis())
    new_ramp = hou.Ramp(bases, source_ramp.keys(), source_ramp.values())
    parm.set(new_ramp)


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


def openLocationFromParm(parm):
    if isinstance(parm, str):
        parm = hou.parm(parm)
    openLocation(parm.eval())


def isExpressionDisabled(parm):
    user_data = parm.node().userDataDict()
    if 'hammer_disabled_expressions' not in user_data:
        return False
    if parm.name() not in json.loads(user_data['hammer_disabled_expressions']):
        return False
    return True


def toggleExpression(parm):
    languages = {'python': hou.exprLanguage.Python,
                 'hscript': hou.exprLanguage.Hscript}
    if isExpressionDisabled(parm):
        user_data = json.loads(parm.node().userData('hammer_disabled_expressions'))
        data = user_data[parm.name()]
        parm.setExpression(data['expression'], languages[data['language']])
        del user_data[parm.name()]
        parm.node().setUserData('hammer_disabled_expressions', json.dumps(user_data))
    else:
        expression = parm.expression()
        language = parm.expressionLanguage()
        data = {'expression': expression,
                'language': 'python' if language == hou.exprLanguage.Python else 'hscript'}
        source_data = parm.node().userData('hammer_disabled_expressions')
        if source_data is not None:
            source_data = json.loads(source_data)
        else:
            source_data = {}
        source_data[parm.name()] = data
        parm.node().setUserData('hammer_disabled_expressions', json.dumps(source_data))
        parm.deleteAllKeyframes()
