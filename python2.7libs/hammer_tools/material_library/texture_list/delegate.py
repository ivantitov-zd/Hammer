try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
    from PyQt5.QtCore import Qt, QSize, QRect, QPoint
    from PyQt5.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle
    from PySide2.QtCore import Qt, QSize, QRect, QPoint
    from PySide2.QtGui import QColor

from ..data_roles import InternalDataRole
from ..texture_map import MapType

MARGIN_SIZE = 4
ICON_SIZE = 64


class TextureDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        return QSize(120, ICON_SIZE + MARGIN_SIZE * 2)

    def paint(self, painter, option, index):
        # painter: QPainter
        # option: QStyleOptionViewItem
        # index: QModelIndex

        texture = index.data(InternalDataRole)

        selected = option.state & QStyle.State_Selected
        if selected or option.state & QStyle.State_HasFocus:
            option.state = option.state & ~QStyle.State_Selected
            painter.save()
            painter.setBrush(QColor(36, 36, 36) if selected else Qt.transparent)
            painter.setPen(QColor(185, 134, 32))
            adjust = painter.pen().width()
            painter.drawRect(option.rect.adjusted(adjust, adjust, -adjust, -adjust))
            painter.restore()

        painter.save()

        rect = option.rect
        inner_rect = rect.adjusted(MARGIN_SIZE, MARGIN_SIZE, -MARGIN_SIZE, -MARGIN_SIZE)
        icon_rect = QRect(inner_rect)
        icon_rect.setWidth(ICON_SIZE)
        map_type_rect = QRect(inner_rect).adjusted(ICON_SIZE + MARGIN_SIZE, 0, 0, 0)
        text_height = 16
        spacing = 2
        map_type_rect.setHeight(text_height)
        texture_name_rect = QRect(map_type_rect)
        texture_name_rect.translate(0, text_height + spacing)
        texture_formats_rect = QRect(texture_name_rect)
        texture_formats_rect.translate(0, text_height + spacing)

        painter.fillRect(icon_rect, Qt.red)
        painter.drawText(map_type_rect, Qt.AlignLeft | Qt.AlignTop, MapType.name(texture.type()))
        painter.drawText(texture_name_rect, Qt.AlignLeft | Qt.AlignTop, texture.name())
        painter.drawText(texture_formats_rect, Qt.AlignLeft | Qt.AlignTop,
                         ' '.join(str(fmt) for fmt in texture.formats()))

        painter.restore()
