try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QApplication
    from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QEvent
    from PyQt5.QtGui import QColor, QImage, QCursor, QPainter, QIcon
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle, QApplication
    from PySide2.QtCore import Qt, QRect, QPoint, QSize, QEvent
    from PySide2.QtGui import QColor, QImage, QCursor, QPainter

import hou

from ..data_roles import FavoriteRole, InternalDataRole
from ..image import loadImage
from ..texture import TextureMap
from ..material import Material
from ..engine_connector import EngineConnector

FAVORITE_ENABLED_ICON = hou.qt.Icon('BUTTONS_favorites', 24, 24)
FAVORITE_DISABLED_ICON = hou.qt.Icon('BUTTONS_not_favorites', 24, 24)
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
        current_item = index.data(InternalDataRole)

        rect = option.rect
        rect_indented = rect.adjusted(MARGIN_SIZE, MARGIN_SIZE, -MARGIN_SIZE, -MARGIN_SIZE)
        top_right_icon_rect = QRect(rect_indented.right() - 24, rect_indented.top(), 24, 24)

        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if top_right_icon_rect.contains(event.pos()):
                current_item.markAsFavorite(None)
                option.widget.update(index)
                return True

        if QApplication.queryKeyboardModifiers() != Qt.ControlModifier:
            if self._zoomed:
                self._zoomed = False
                option.widget.update(index)
            return False

        self._zoomed = True

        if current_item == self._previous_item:
            option.widget.update(index)
            return False

        if isinstance(current_item, Material):
            icon = current_item.thumbnail(EngineConnector.currentEngine())
            if icon:
                self._image = icon.pixmap(256).toImage()
            else:
                self._image = None
        elif isinstance(current_item, TextureMap):
            self._image = loadImage(current_item.path())
        else:
            return False

        self._previous_item = current_item
        option.widget.update(index)
        return False

    def paint(self, painter, option, index):
        current_item = index.data(InternalDataRole)
        selected = option.state & QStyle.State_Selected
        has_focus = option.state & QStyle.State_HasFocus
        under_cursor = option.state & QStyle.State_MouseOver

        rect = option.rect

        rect_indented = rect.adjusted(MARGIN_SIZE, MARGIN_SIZE, -MARGIN_SIZE, -MARGIN_SIZE)

        top_right_icon_rect = QRect(rect_indented.right() - 24, rect_indented.top(), 24, 24)

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

        if self._image and isinstance(current_item, (TextureMap, Material)) and under_cursor and \
                QApplication.queryKeyboardModifiers() == Qt.ControlModifier:
            # Draw zoomed texture
            cursor_pos = option.widget.mapFromGlobal(QCursor.pos()) - thumbnail_rect.topLeft()
            texture_width = self._image.width()
            texture_height = self._image.height()
            sample_width = max(texture_width * 0.2, thumbnail_rect.width())
            sample_height = max(texture_height * 0.2, thumbnail_rect.height())

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
                FAVORITE_ENABLED_ICON.paint(painter, rect_indented, Qt.AlignTop | Qt.AlignRight)
            elif under_cursor:
                FAVORITE_DISABLED_ICON.paint(painter, top_right_icon_rect)

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
