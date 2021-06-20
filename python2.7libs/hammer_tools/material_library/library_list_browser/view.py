try:
    from PyQt5.QtWidgets import QListView
    from PyQt5.QtGui import QFont
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QListView
    from PySide2.QtGui import QFont
    from PySide2.QtCore import Qt

from .delegate import LibraryDelegate


class LibraryListView(QListView):
    def __init__(self):
        super(LibraryListView, self).__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        self.setItemDelegate(LibraryDelegate())
