try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *


class LibraryListView(QListView):
    def __init__(self):
        super(LibraryListView, self).__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
