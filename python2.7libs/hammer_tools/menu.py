try:
    from PyQt5.QtWidgets import QMenu
    from PyQt5.QtGui import QCursor
    from PyQt5.QtCore import QTimer, QPoint
except ImportError:
    from PySide2.QtWidgets import QMenu
    from PySide2.QtGui import QCursor
    from PySide2.QtCore import QTimer, QPoint


class Menu(QMenu):
    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)
        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._hideByDistance)
        self._dist_limit = 300

    def _hideByDistance(self):
        if (self.geometry().center() - QCursor.pos()).manhattanLength() > self._dist_limit:
            self.hide()

    def showEvent(self, event):
        size = self.sizeHint()
        self._dist_limit = QPoint(size.width(), size.height()).manhattanLength()
        self._timer.start()
        super(Menu, self).showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super(Menu, self).hideEvent(event)
