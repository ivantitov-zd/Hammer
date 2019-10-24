from __future__ import print_function

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class FilterField(QLineEdit):
    def __init__(self):
        super(FilterField, self).__init__()

        self.setFrame(False)

        self.setPlaceholderText('Type to Filter...')


class FontListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(FontListModel, self).__init__(parent)

        self.font_list = None

    def rowCount(self, parent):
        return len(self.font_list)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.font_list[index.row()]
        elif role == Qt.UserRole or Qt.ToolTipRole:
            return self.font_list[index.row()]


class FontLabelDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(FontLabelDelegate, self).__init__(parent)

        self.textOption = QTextOption()
        self.textOption.setWrapMode(QTextOption.NoWrap)

    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(172, 206, 247))
        text = index.data(Qt.DisplayRole)
        font_name = index.data(Qt.UserRole)
        font_tokens = font_name.lower().split()
        font = QFont(font_name, 12)

        # Stretch
        if 'condensed' in font_tokens or 'cond' in font_tokens:
            font.setStretch(QFont.Condensed)
        # Style
        if 'italic' in font_tokens:
            font.setItalic(True)
        elif 'oblique' in font_tokens:
            font.setStyle(QFont.StyleOblique)

        # Weight
        if 'thin' in font_tokens:
            font.setWeight(QFont.Thin)
        elif 'light' in font_tokens:
            font.setWeight(QFont.Light)
        elif 'extralight' in font_tokens:
            font.setWeight(QFont.ExtraLight)
        elif 'normal' in font_tokens:
            font.setWeight(QFont.Normal)
        elif 'medium' in font_tokens:
            font.setWeight(QFont.Medium)
        elif 'bold' in font_tokens:
            font.setWeight(QFont.Bold)
        elif 'demibold' in font_tokens or 'semibold' in font_tokens or 'demi' in font_tokens or 'semi' in font_tokens:
            font.setWeight(QFont.DemiBold)
        elif 'black' in font_tokens or 'heavy' in font_tokens or 'extrabold' in font_tokens:
            font.setWeight(QFont.Black)

        painter.setFont(font)
        painter.setRenderHints(QPainter.TextAntialiasing)
        font_height = QFontMetrics(font).height()
        rect = option.rect
        painter.drawText(QRectF(5, rect.top() + rect.height() / 2 - font_height / 2, rect.width() - 5, font_height), text, self.textOption)

    def sizeHint(self, option, index):
        return QSize(300, 30)


class FontListView(QListView):
    def __init__(self):
        super(FontListView, self).__init__()

        self.setFrameStyle(self.NoFrame)

        self.setItemDelegate(FontLabelDelegate(self))


class SelectFontDialog(QDialog):
    def __init__(self):
        super(SelectFontDialog, self).__init__()
        self.parm = None
        self.previous_value = None

        self.setWindowTitle('Select Font')
        self.setProperty('houdiniStyle', True)

        # Font List
        self.font_list_model = FontListModel(self)
        font_list_filter_model = QSortFilterProxyModel(self)
        font_list_filter_model.setSourceModel(self.font_list_model)
        font_list_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.font_list_view = FontListView()
        self.font_list_view.setModel(font_list_filter_model)
        selectionModel = self.font_list_view.selectionModel()
        selectionModel.currentChanged.connect(self.apply)
        self.font_list_view.doubleClicked.connect(self.accept)

        # Filter Field
        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(lambda p: font_list_filter_model.setFilterWildcard('*' + p + '*'))

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.filter_field)
        main_layout.addWidget(self.font_list_view)

    def show(self, parm):
        self.parm = parm
        self.previous_value = parm.eval()
        self.font_list_model.beginResetModel()
        self.font_list_model.font_list = parm.menuItems()
        self.font_list_model.endResetModel()
        super(SelectFontDialog, self).show()

    def exec_(self, parm):
        self.parm = parm
        self.previous_value = parm.eval()
        super(SelectFontDialog, self).exec_()

    def apply(self, index):
        self.parm.set(index.data(Qt.UserRole))

    def reject(self):
        self.parm.set(self.previous_value)
        super(SelectFontDialog, self).reject()


def select(parm):
    if not hasattr(hou.session, 'hammer_select_font_dialog'):
        hou.session.hammer_select_font_dialog = SelectFontDialog()
    hou.session.hammer_select_font_dialog.show(parm)
