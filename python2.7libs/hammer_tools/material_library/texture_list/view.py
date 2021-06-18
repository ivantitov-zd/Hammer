try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from .delegate import TextureDelegate


class TextureListView(QListView):
    def __init__(self):
        super(TextureListView, self).__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setItemDelegate(TextureDelegate(self))
