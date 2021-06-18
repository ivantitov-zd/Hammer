try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QApplication
    from PyQt5.QtCore import Qt, QRect, QPoint, QSize
    from PyQt5.QtGui import QColor, QImage, QCursor, QPainter, QIcon
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle, QApplication
    from PySide2.QtCore import Qt, QRect, QPoint, QSize
    from PySide2.QtGui import QColor, QImage, QCursor, QPainter

import hou

from ..data_roles import FavoriteRole, InternalDataRole
from ..texture import TextureMap
from ..image import loadImage

FAVORITE_ICON = hou.qt.Icon('BUTTONS_favorites', 24, 24)
ZOOM_ICON = hou.qt.Icon('IMAGE_zoom_in', 24, 24)

MARGIN_SIZE = 4


# painter: QPainter
# option: QStyleOptionViewItem
# index: QModelIndex

class LibraryItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(LibraryItemDelegate, self).__init__(parent)

        self._previous_item = None
        self._image = None
        self._zoomed = False

    def editorEvent(self, event, model, option, index):
        if QApplication.queryKeyboardModifiers() != Qt.ControlModifier:
            if self._zoomed:
                self._zoomed = False
                option.widget.update()
            return False

        self._zoomed = True

        current_item = index.data(InternalDataRole)
        if not isinstance(current_item, TextureMap):
            return False

        if current_item != self._previous_item:
            self._previous_item = current_item
            self._image = loadImage(current_item.path())

        option.widget.update(index)
        return False

    def paint(self, painter, option, index):
        current_item = index.data(InternalDataRole)
        selected = option.state & QStyle.State_Selected
        has_focus = option.state & QStyle.State_HasFocus

        rect = option.rect

        rect_indented = rect.adjusted(MARGIN_SIZE, MARGIN_SIZE, -MARGIN_SIZE, -MARGIN_SIZE)

        thumbnail_rect = QRect()
        thumbnail_rect.setSize(option.decorationSize)
        thumbnail_rect.moveCenter(QPoint(rect.center().x(), option.decorationSize.height() / 2 + rect.y() + 2))

        text_rect = QRect(rect)
        text_rect.setTop(thumbnail_rect.bottom())

        painter.save()
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.setClipping(True)
        painter.setClipRect(rect)

        painter.eraseRect(rect)

        # Draw darker background
        if selected:
            painter.save()
            painter.setBrush(QColor(36, 36, 36))
            painter.setPen(Qt.NoPen)
            adjust = painter.pen().width() / 2
            painter.drawRect(rect.adjusted(adjust, adjust, -adjust, -adjust))
            painter.restore()

        if self._image and isinstance(current_item, TextureMap) and \
                option.state & QStyle.State_MouseOver and \
                QApplication.queryKeyboardModifiers() == Qt.ControlModifier:
            # Draw zoomed texture
            cursor_pos = option.widget.mapFromGlobal(QCursor.pos()) - thumbnail_rect.topLeft()
            texture_width = self._image.width()
            texture_height = self._image.height()
            sample_width = texture_width * 0.2
            sample_height = texture_height * 0.2

            max_x = texture_width - sample_width
            max_y = texture_height - sample_height
            sample_top_left = QPoint(
                hou.hmath.clamp(cursor_pos.x() / float(thumbnail_rect.width()) * max_x, 0, max_x),
                hou.hmath.clamp(cursor_pos.y() / float(thumbnail_rect.height()) * max_y, 0, max_y)
            )
            image = self._image.copy(QRect(sample_top_left, QSize(sample_width, sample_height)))
            painter.drawImage(thumbnail_rect.topLeft(),
                              image.scaled(option.decorationSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

            ZOOM_ICON.paint(painter, rect_indented, Qt.AlignTop | Qt.AlignRight)
        else:
            # Draw thumbnail
            thumbnail = index.data(Qt.DecorationRole)
            thumbnail.paint(painter, thumbnail_rect)

            # Draw favorite icon
            if index.data(FavoriteRole):
                FAVORITE_ICON.paint(painter, rect_indented, Qt.AlignTop | Qt.AlignRight)

        # Draw text
        metrics = painter.fontMetrics()
        text = metrics.elidedText(index.data(Qt.DisplayRole), Qt.ElideRight, text_rect.adjusted(4, 0, -4, 0).width())
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(text_rect, Qt.AlignCenter, text)

        # Draw frame
        if selected or has_focus:
            painter.setBrush(Qt.transparent)
            painter.setPen(QColor(185, 134, 32))
            adjust = painter.pen().width()
            painter.drawRect(rect.adjusted(adjust, adjust, -adjust, -adjust))

        painter.restore()
