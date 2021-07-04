try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from . import ui


class SaveThumbnailsOptionsWindow(QDialog):
    def __init__(self, parent=None):
        super(SaveThumbnailsOptionsWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('Save thumbnails')
        self.setWindowIcon(ui.icon('BUTTONS_save_image', 32))
        self.resize(400, 300)

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
