try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

from .model import TextureListModel
from .view import TextureListView


class TextureListBrowser(QDialog):
    def __init__(self, parent=None):
        super(TextureListBrowser, self).__init__(parent)

        self.setWindowTitle('Textures')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.model = TextureListModel()

        self.view = TextureListView()
        self.view.setModel(self.model)
        layout.addWidget(self.view)

    def updateContent(self):
        self.model.updateLibraryList()
