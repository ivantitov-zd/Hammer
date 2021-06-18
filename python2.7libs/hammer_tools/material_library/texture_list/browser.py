try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou

from .model import TextureListModel
from .view import TextureListView


class TextureListBrowser(QDialog):
    def __init__(self, parent=None):
        super(TextureListBrowser, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle('Textures')
        self.setWindowIcon(hou.qt.Icon('BUTTONS_parmmenu_texture', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.model = TextureListModel()

        self.view = TextureListView()
        self.view.setModel(self.model)
        layout.addWidget(self.view)

    def reloadContent(self):
        self.model.updateLibraryList()
