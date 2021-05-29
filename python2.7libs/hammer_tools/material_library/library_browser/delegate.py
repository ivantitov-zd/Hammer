try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor

import hou

from .model import FavoriteRole

FAVORITE_ICON = hou.qt.Icon('BUTTONS_favorites', 24, 24)


class MaterialDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # painter: QPainter
        # option: QStyleOptionViewItem
        # index: QModelIndex
        selected = option.state & QStyle.State_Selected
        option.state = option.state & ~QStyle.State_Selected

        if selected:
            painter.save()
            painter.setBrush(QColor(36, 36, 36))
            painter.setPen(Qt.NoPen)
            adjust = painter.pen().width()
            painter.drawRect(option.rect.adjusted(adjust, adjust, -adjust, -adjust))
            painter.restore()

        super(MaterialDelegate, self).paint(painter, option, index)

        if selected or option.state & QStyle.State_HasFocus:
            painter.save()
            painter.setBrush(Qt.transparent)
            painter.setPen(QColor(185, 134, 32))
            adjust = painter.pen().width()
            painter.drawRect(option.rect.adjusted(adjust, adjust, -adjust, -adjust))
            painter.restore()

        if index.data(FavoriteRole):
            FAVORITE_ICON.paint(painter, option.rect.adjusted(4, 4, -4, -4), Qt.AlignTop | Qt.AlignRight)
