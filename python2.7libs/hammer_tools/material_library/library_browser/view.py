try:
    from PyQt5.QtWidgets import QListView, QAbstractItemView
    from PyQt5.QtGui import QPainter, QFont, QColor
    from PyQt5.QtCore import Qt, QModelIndex, QEvent, QSize
except ImportError:
    from PySide2.QtWidgets import QListView, QAbstractItemView
    from PySide2.QtGui import QPainter, QFont, QColor
    from PySide2.QtCore import Qt, QModelIndex, QEvent, QSize

from .delegate import MaterialDelegate


class LibraryView(QListView):
    def __init__(self):
        super(LibraryView, self).__init__()

        self.setViewMode(QListView.IconMode)
        self.setUniformItemSizes(True)
        self.viewport().installEventFilter(self)

        self.setResizeMode(QListView.Adjust)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragEnabled(True)

        self.setItemDelegate(MaterialDelegate())

    def library(self):
        return self.model().library()

    def setLibrary(self, library):
        self.model().setLibrary(library)

    def scrollToCurrent(self):
        if self.currentIndex().isValid():
            self.scrollTo(self.currentIndex(), QAbstractItemView.PositionAtCenter)

    def setIconSize(self, size):
        super(LibraryView, self).setIconSize(size)
        self.scrollToCurrent()

    def resizeEvent(self, event):
        super(LibraryView, self).resizeEvent(event)
        self.scrollToCurrent()

    def zoomIn(self, amount=8):
        size = min(self.iconSize().width() + amount, 256)
        self.setIconSize(QSize(size, size))

    def zoomOut(self, amount=8):
        size = max(self.iconSize().width() - amount, 48)
        self.setIconSize(QSize(size, size))

    def eventFilter(self, watched, event):
        if watched == self.viewport() and event.type() == QEvent.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                if event.delta() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
                return True
        return False

    def paintEvent(self, event):
        text = None
        if self.model() is None:
            text = 'No data source'
        elif self.model().library() is None:
            text = 'No library selected'
        elif self.model().rowCount(QModelIndex()) <= 0:
            text = 'No items'

        if text:
            painter = QPainter(self.viewport())
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            painter.setPen(QColor(68, 68, 68))
            painter.drawText(self.rect(), Qt.AlignCenter, text)
        else:
            return super(LibraryView, self).paintEvent(event)
