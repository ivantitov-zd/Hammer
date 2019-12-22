from __future__ import print_function

from hammer_tools.utils import fuzzyMatch

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class FilterField(QLineEdit):
    # Signals
    downPressed = Signal()
    accepted = Signal()

    def __init__(self):
        super(FilterField, self).__init__()

        self.setPlaceholderText('Type to Filter...')

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.clear()
        elif key == Qt.Key_Down:
            self.downPressed.emit()
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit()
        else:
            super(FilterField, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
            self.clear()
        super(FilterField, self).mousePressEvent(event)


class FuzzyFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FuzzyFilterProxyModel, self).__init__(parent)

        self.__filter_pattern = ''

    def setFilterPattern(self, pattern):
        self.beginResetModel()
        if self.filterCaseSensitivity() == Qt.CaseInsensitive:
            self.__filter_pattern = pattern.lower()
        else:
            self.__filter_pattern = pattern
        self.endResetModel()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        text = source_model.data(source_model.index(source_row, 0, source_parent), Qt.DisplayRole)
        return fuzzyMatch(self.__filter_pattern, text if self.filterCaseSensitivity() == Qt.CaseSensitive else text.lower())[0]


class FontLabelDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(FontLabelDelegate, self).__init__(parent)

        self.textOption = QTextOption()
        self.textOption.setWrapMode(QTextOption.NoWrap)

    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.color(QPalette.Highlight))
        text = index.data(Qt.DisplayRole)
        font_name = text
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


class SelectListView(QListView):
    # Signals
    accepted = Signal()

    def __init__(self):
        super(SelectListView, self).__init__()

        self.setFrameStyle(self.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit()
        else:
            super(SelectListView, self).keyPressEvent(event)


class SelectDialog(QDialog):
    def __init__(self, parent):
        super(SelectDialog, self).__init__(parent, Qt.Window)
        self.parm = None
        self.previous_value = None

        self.setWindowTitle('Select')
        self.resize(300, 600)
        self.setProperty('houdiniStyle', True)
        self.setStyleSheet(hou.qt.styleSheet())

        # List
        self.list_model = QStringListModel(self)
        self.list_filter_model = FuzzyFilterProxyModel(self)
        self.list_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.list_filter_model.setSourceModel(self.list_model)

        self.list_view = SelectListView()
        self.list_view.setModel(self.list_filter_model)
        self.selectionModel = self.list_view.selectionModel()
        self.selectionModel.currentChanged.connect(self.apply)
        self.list_view.doubleClicked.connect(self.accept)
        self.list_view.accepted.connect(self.accept)

        # Filter
        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(self.list_filter_model.setFilterPattern)
        self.filter_field.downPressed.connect(self.switchToList)
        self.filter_field.accepted.connect(self.acceptFromFilterField)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        main_layout.addWidget(self.filter_field)
        main_layout.addWidget(self.list_view)

    def switchToList(self):
        self.list_view.setFocus()
        self.selectionModel.select(self.list_filter_model.index(0, 0), QItemSelectionModel.Select)

    def acceptFromFilterField(self):
        print(self.list_filter_model.rowCount())
        if self.list_filter_model.rowCount() == 1:
            self.accept()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == Qt.Key_F3 or key == Qt.Key_F and modifiers == Qt.ControlModifier:
            self.filter_field.setFocus()
            self.filter_field.selectAll()
        super(SelectDialog, self).keyPressEvent(event)

    def show(self, parm):
        self.parm = parm
        self.previous_value = parm.eval()
        self.list_model.setStringList(parm.menuItems())
        self.filter_field.setFocus()
        super(SelectDialog, self).show()

    def apply(self, index):
        self.parm.set(index.data(Qt.DisplayRole))

    def reject(self):
        self.parm.set(self.previous_value)
        super(SelectDialog, self).reject()


class SelectFontDialog(SelectDialog):
    def __init__(self, parent=None):
        super(SelectFontDialog, self).__init__(parent)

        self.setWindowTitle('Select Font')

        self.list_view.setItemDelegate(FontLabelDelegate(self))


def selectAny(parm):
    if not hasattr(hou.session, 'hammer_select_dialog'):
        hou.session.hammer_select_dialog = SelectDialog(hou.qt.mainWindow())
    hou.session.hammer_select_dialog.show(parm)


def selectFont(parm):
    if not hasattr(hou.session, 'hammer_select_font_dialog'):
        hou.session.hammer_select_font_dialog = SelectFontDialog(hou.qt.mainWindow())
    hou.session.hammer_select_font_dialog.show(parm)
