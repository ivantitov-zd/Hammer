try:
    from PyQt5.QtWidgets import QListView, QAbstractItemView, QApplication
    from PyQt5.QtGui import QPainter, QFont, QColor
    from PyQt5.QtCore import Qt, QModelIndex, QEvent, QSize, QPropertyAnimation, QEasingCurve
except ImportError:
    from PySide2.QtWidgets import QListView, QAbstractItemView, QApplication
    from PySide2.QtGui import QPainter, QFont, QColor
    from PySide2.QtCore import Qt, QModelIndex, QEvent, QSize, QPropertyAnimation, QEasingCurve

from .. import ui
from .delegate import LibraryItemDelegate


class LibraryView(QListView):
    def __init__(self):
        super(LibraryView, self).__init__()

        self.setViewMode(QListView.IconMode)
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

        self.setResizeMode(QListView.Adjust)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._animation = QPropertyAnimation(self.verticalScrollBar(), 'value')
        self._animation.setDuration(200)
        self._old_value = 0
        self.verticalScrollBar().valueChanged.connect(self._animate)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragEnabled(True)

        self.setItemDelegate(LibraryItemDelegate(self))

    def _animate(self, new_value):
        if QApplication.queryKeyboardModifiers() == Qt.ControlModifier:
            if self._animation.state() == QPropertyAnimation.Running:
                self._old_value = self._animation.currentValue()
                self._animation.stop()
            return

        if self._animation.state() == QPropertyAnimation.Running:
            if self._animation.currentValue() == new_value:
                return
            else:
                self._old_value = self._animation.currentValue()
                self._animation.stop()

        self._animation.setStartValue(self._old_value)
        self._animation.setEndValue(new_value)
        if abs(new_value - self._old_value) > self.iconSize().height() * 5:
            self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        else:
            self._animation.setEasingCurve(QEasingCurve.OutSine)
        self._old_value = new_value
        self._animation.start()

    def library(self):
        return self.model().library()

    def setLibrary(self, library):
        self.model().setLibrary(library)

    def scrollToCurrent(self):
        if self.currentIndex().isValid():
            self.scrollTo(self.currentIndex(), QAbstractItemView.PositionAtCenter)

    def setIconSize(self, size):
        super(LibraryView, self).setIconSize(QSize(size, size))
        self.verticalScrollBar().setSingleStep(int(size / 2.5))
        self.scrollToCurrent()

    def resizeEvent(self, event):
        super(LibraryView, self).resizeEvent(event)
        self.scrollToCurrent()

    def zoomIn(self, amount=8):
        size = min(self.iconSize().width() + amount, 256)
        self.setIconSize(size)

    def zoomOut(self, amount=8):
        size = max(self.iconSize().width() - amount, 48)
        self.setIconSize(size)

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
            font.setPointSize(ui.scaled(16))
            painter.setFont(font)
            painter.setPen(QColor(68, 68, 68))
            painter.drawText(self.rect(), Qt.AlignCenter, text)
        else:
            return super(LibraryView, self).paintEvent(event)
