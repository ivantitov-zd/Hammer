try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
    from PyQt5.QtCore import Qt, QSize, QRect, QPoint
    from PyQt5.QtGui import QColor, QPainter
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle
    from PySide2.QtCore import Qt, QSize, QRect, QPoint
    from PySide2.QtGui import QColor, QPainter

from ..data_roles import InternalDataRole
from ..image import loadImage
from ..texture import MapType, MISSING_TEXTURE_THUMBNAIL_ICON

MARGIN_SIZE = 4
THUMBNAIL_SIZE = 64


# painter: QPainter
# option: QStyleOptionViewItem
# index: QModelIndex

class TextureDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(TextureDelegate, self).__init__(parent)

        self._thumbnail_cache = {}

    def sizeHint(self, option, index):
        return QSize(120, THUMBNAIL_SIZE + 2 * MARGIN_SIZE)

    def paint(self, painter, option, index):
        texture = index.data(InternalDataRole)
        if texture not in self._thumbnail_cache:
            image = loadImage(texture.path())
            if image:
                image = image.scaled(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE),
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._thumbnail_cache[texture] = image

        selected = option.state & QStyle.State_Selected
        has_focus = option.state & QStyle.State_HasFocus

        rect = option.rect

        rect_indented = rect.adjusted(MARGIN_SIZE, MARGIN_SIZE, -MARGIN_SIZE, -MARGIN_SIZE)

        thumbnail_rect = QRect(rect_indented)
        thumbnail_rect.setWidth(THUMBNAIL_SIZE)

        text_height = 16
        spacing = rect_indented.height() / 3 - text_height

        map_type_rect = QRect(rect_indented).adjusted(THUMBNAIL_SIZE + MARGIN_SIZE, 0, 0, 0)
        map_type_rect.setHeight(text_height)

        texture_name_rect = QRect(map_type_rect)
        texture_name_rect.translate(0, text_height + spacing)

        texture_formats_rect = QRect(texture_name_rect)
        texture_formats_rect.translate(0, text_height + spacing)

        painter.save()
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.setClipping(True)
        painter.setClipRect(rect)

        painter.eraseRect(rect)

        if selected or has_focus:
            option.state = option.state & ~QStyle.State_Selected
            painter.save()
            painter.setBrush(QColor(36, 36, 36) if selected else Qt.transparent)
            painter.setPen(QColor(185, 134, 32))
            adjust = painter.pen().width()
            painter.drawRect(option.rect.adjusted(adjust, adjust, -adjust, -adjust))
            painter.restore()

        thumbnail = self._thumbnail_cache[texture] or MISSING_TEXTURE_THUMBNAIL_ICON
        painter.drawImage(thumbnail_rect.topLeft(), thumbnail)
        painter.drawText(map_type_rect, Qt.AlignLeft | Qt.AlignTop, MapType.name(texture.type()))
        painter.drawText(texture_name_rect, Qt.AlignLeft | Qt.AlignTop, texture.name())
        painter.drawText(texture_formats_rect, Qt.AlignLeft | Qt.AlignTop,
                         ' '.join(str(fmt) for fmt in texture.formats()))

        painter.restore()
