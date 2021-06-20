try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor


class LibraryDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        selected = option.state & QStyle.State_Selected
        has_focus = option.state & QStyle.State_HasFocus

        rect = option.rect

        margin = painter.pen().width()
        rect_indented = rect.adjusted(margin, margin, -margin, -margin)

        if selected or has_focus:
            painter.save()
            painter.setBrush(QColor(36, 36, 36))
            painter.setPen(QColor(185, 134, 32))
            painter.drawRect(rect_indented)
            painter.restore()

        painter.drawText(rect_indented.adjusted(4, 0, 0, 0),
                         Qt.AlignVCenter | Qt.AlignLeft,
                         index.data(Qt.DisplayRole))
