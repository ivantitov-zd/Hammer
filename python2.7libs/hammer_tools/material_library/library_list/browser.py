try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from ..data_roles import InternalDataRole
from ..library import Library
from .model import LibraryListModel
from .view import LibraryListView


class LibraryListBrowser(QWidget):
    currentLibraryChanged = Signal(Library)

    def __init__(self):
        super(LibraryListBrowser, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.model = LibraryListModel()

        self.view = LibraryListView()
        self.view.setModel(self.model)
        selection_model = self.view.selectionModel()
        selection_model.currentChanged.connect(self.emitCurrentLibraryChanged)
        layout.addWidget(self.view)

    def updateContent(self):
        self.model.updateLibraryList()

    def emitCurrentLibraryChanged(self, index):
        self.currentLibraryChanged.emit(index.data(InternalDataRole))
