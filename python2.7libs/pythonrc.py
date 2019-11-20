from __future__ import print_function

import hdefereval
import hou

from hammer_tools.previous_files import setSessionWatcher, show


def instant():
    setSessionWatcher()


instant()


def afterUserInterface():
    show()


if hou.isUIAvailable():
    hdefereval.executeDeferred(afterUserInterface)
