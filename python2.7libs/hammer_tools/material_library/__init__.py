import hou


def fakeIcon(*args, **kwargs):
    try:
        return hou.qt.createIcon(*args, **kwargs)
    except hou.OperationFailed:
        return hou.qt.createIcon('SOP_python', 16, 16)


hou.qt.Icon = fakeIcon
from .viewer_window import MaterialLibraryViewerDialog
