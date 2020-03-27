from __future__ import print_function

import hdefereval
import hou

from hammer_tools.previous_files import setSessionWatcher, showPreviousFiles
from hammer_tools.settings import SettingsManager

settings = SettingsManager.instance()


def instant():
    setSessionWatcher()


instant()


def afterUserInterface():
    if settings.value('hammer.previous_files.startup') and \
            hou.hipFile.basename().startswith('untitled.hip'):
        showPreviousFiles()


if hou.isUIAvailable():
    hdefereval.executeDeferred(afterUserInterface)
