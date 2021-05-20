try:
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtCore import Qt

InternalDataRole = Qt.UserRole + 10
FavoriteRole = Qt.UserRole + 11
CommentRole = Qt.UserRole + 12
