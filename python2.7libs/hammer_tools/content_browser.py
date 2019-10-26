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

from hammer_tools.utils import createAction


def isRevertToDefaultEvent(event):
    return event.modifiers() == Qt.ControlModifier and event.button() == Qt.MiddleButton


class Slider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(Slider, self).__init__(orientation, parent)
        self.defaultValue = 0
        self.valueLadderMode = False

    def revertToDefault(self):
        self.setValue(self.defaultValue)

    def setDefaultValue(self, value, reset=True):
        self.defaultValue = value
        if reset:
            self.revertToDefault()

    def mousePressEvent(self, event):
        if False:  # Type hint
            event = QMouseEvent
        if event.button() == Qt.MiddleButton:
            return
        elif event.button() == Qt.LeftButton:
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier)
        super(Slider, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if False:  # Type hint
            event = QMouseEvent
        if not self.valueLadderMode and event.buttons() == Qt.MiddleButton:
            try:
                hou.ui.openValueLadder(self.value(), self.setValue, data_type=hou.valueLadderDataType.Int)
            except hou.OperationFailed:
                return
            else:
                self.valueLadderMode = True
        elif self.valueLadderMode:
            hou.ui.updateValueLadder(event.globalX(), event.globalY(),
                                     bool(event.modifiers() & Qt.AltModifier),
                                     bool(event.modifiers() & Qt.ShiftModifier))
        else:
            super(Slider, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if False:  # Type hint
            event = QMouseEvent
        if self.valueLadderMode and event.button() == Qt.MiddleButton:
            hou.ui.closeValueLadder()
            self.valueLadderMode = False
        elif isRevertToDefaultEvent(event):
            self.revertToDefault()
        else:
            super(Slider, self).mouseReleaseEvent(event)


class SearchField(QComboBox):
    def __init__(self, parent=None):
        super(SearchField, self).__init__(parent)

        self.setEditable(True)
        edit = self.lineEdit()
        edit.setPlaceholderText('Search...')
        edit.installEventFilter(self)
        edit.setFont(QFont('Segoe UI'))
        self.setFixedHeight(26)
        comp = self.completer()
        comp.setCompletionMode(QCompleter.PopupCompletion)
        comp.setFilterMode(Qt.MatchContains)
        comp.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        comp.setMaxVisibleItems(5)
        popup = comp.popup()
        popup.setStyleSheet(hou.qt.styleSheet())

    def mouseReleaseEvent(self, event):
        if False:  # Type hint
            event = QMouseEvent
        if isRevertToDefaultEvent(event):
            self.clearEditText()

    def eventFilter(self, watched, event):
        if False:  # Type hint
            watched = QObject
            event = QEvent
        if watched == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease and isRevertToDefaultEvent(event):
                self.clearEditText()
                event.accept()
                return True
        return False

    def keyPressEvent(self, event):
        if False:  # Type hint
            event = QKeyEvent
        key = event.key()
        mod = event.modifiers()
        if mod == Qt.NoModifier and key == Qt.Key_Escape:
            self.clearEditText()
        else:
            super(SearchField, self).keyPressEvent(event)

    def hidePopup(self):
        super(SearchField, self).hidePopup()
        self.lineEdit().setFocus()

link_or_state_icon = 'BUTTONS_link'
embedded_icon = 'BUTTONS_pinned'

class BrowserMode(QStandardItemModel):
    def __init__(self):
        super(BrowserMode, self).__init__()


class BrowserTreeView(QTreeView):
    def __init__(self, parent=None):
        super(BrowserTreeView, self).__init__(parent)
        self.setAlternatingRowColors(True)


class BrowserTableView(QListView):
    def __init__(self, parent=None):
        super(BrowserTableView, self).__init__(parent)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setIconSize(QSize(120, 90))
        self.setUniformItemSizes(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)


class ContentBrowser(QWidget):
    def __init__(self, parent=None):
        super(ContentBrowser, self).__init__(parent)

        self.setWindowTitle('Content Browser')
        self.setProperty('houdiniStyle', True)

        topLayout = QHBoxLayout()
        topLayout.setContentsMargins(4, 4, 4, 2)
        topLayout.setSpacing(2)

        self.refreshButton = QPushButton()
        self.refreshButton.setFixedSize(26, 26)
        self.refreshButton.setToolTip('Update\tF5')
        self.refreshButton.setIcon(hou.qt.Icon('BUTTONS_reload', 18, 18))
        self.refreshButton.setIconSize(QSize(18, 18))
        topLayout.addWidget(self.refreshButton)

        sep = hou.qt.Separator()
        if False:  # Type hint
            sep = QFrame
        sep.setFixedWidth(2)
        sep.setFrameShape(QFrame.VLine)
        topLayout.addWidget(sep)

        viewModeButtonGroup = QButtonGroup(self)
        viewModeButtonGroup.setExclusive(True)
        self.treeViewButton = QPushButton()
        self.treeViewButton.setFixedSize(26, 26)
        self.treeViewButton.setToolTip('Tree View\t\tCtrl+1')
        self.treeViewButton.setIcon(hou.qt.Icon('BUTTONS_tree', 18, 18))
        self.treeViewButton.setIconSize(QSize(18, 18))
        self.treeViewButton.setCheckable(True)
        viewModeButtonGroup.addButton(self.treeViewButton)
        topLayout.addWidget(self.treeViewButton)

        self.tableViewButton = QPushButton()
        self.tableViewButton.setFixedSize(26, 26)
        self.tableViewButton.setToolTip('Table View\tCtrl+2')
        self.tableViewButton.setIcon(hou.qt.Icon('NETVIEW_shape_palette', 18, 18))
        self.tableViewButton.setIconSize(QSize(18, 18))
        self.tableViewButton.setCheckable(True)
        self.tableViewButton.toggle()
        viewModeButtonGroup.addButton(self.tableViewButton)
        topLayout.addWidget(self.tableViewButton)

        topLayout.addWidget(sep)

        self.searchField = SearchField()
        self.searchField.setToolTip('Search\tCtrl+F, F3')
        topLayout.addWidget(self.searchField)

        searchModeButtonGroup = QButtonGroup(self)
        searchModeButtonGroup.setExclusive(True)

        self.wholeSearchButton = QPushButton()
        self.wholeSearchButton.setFixedSize(26, 26)
        self.wholeSearchButton.setCheckable(True)
        self.wholeSearchButton.setToolTip('Whole word search')
        self.wholeSearchButton.setIcon(hou.qt.Icon('VOP_titlecase', 18, 18))
        self.wholeSearchButton.setIconSize(QSize(18, 18))
        searchModeButtonGroup.addButton(self.wholeSearchButton)
        topLayout.addWidget(self.wholeSearchButton)

        self.fuzzySearchButton = QPushButton()
        self.fuzzySearchButton.setFixedSize(26, 26)
        self.fuzzySearchButton.setCheckable(True)
        self.fuzzySearchButton.toggle()
        self.fuzzySearchButton.setToolTip('Fuzzy search')
        self.fuzzySearchButton.setIcon(hou.qt.Icon('VOP_endswith', 18, 18))
        self.fuzzySearchButton.setIconSize(QSize(18, 18))
        searchModeButtonGroup.addButton(self.fuzzySearchButton)
        topLayout.addWidget(self.fuzzySearchButton)

        self.patternSearchButton = QPushButton()
        self.patternSearchButton.setFixedSize(26, 26)
        self.patternSearchButton.setCheckable(True)
        self.patternSearchButton.setToolTip('Search by Pattern')
        self.patternSearchButton.setIcon(hou.qt.Icon('VOP_isalpha', 18, 18))
        self.patternSearchButton.setIconSize(QSize(18, 18))
        searchModeButtonGroup.addButton(self.patternSearchButton)
        topLayout.addWidget(self.patternSearchButton)

        self.regexSearchButton = QPushButton()
        self.regexSearchButton.setFixedSize(26, 26)
        self.regexSearchButton.setCheckable(True)
        self.regexSearchButton.setToolTip('Search by Regular Expression')
        self.regexSearchButton.setIcon(hou.qt.Icon('VOP_regex_match', 18, 18))
        self.regexSearchButton.setIconSize(QSize(18, 18))
        searchModeButtonGroup.addButton(self.regexSearchButton)
        topLayout.addWidget(self.regexSearchButton)

        topLayout.addWidget(sep)

        topLayout.addWidget(hou.qt.HelpButton('/hammer/content_browser', 'Show Help\tF1'))

        middleLayout = QHBoxLayout()
        middleLayout.setContentsMargins(4, 0, 0, 4)
        middleLayout.setSpacing(4)

        self.viewLayout = QStackedLayout(middleLayout)
        model = QFileSystemModel()
        model.setRootPath('C:/')

        treeView = BrowserTreeView()
        treeView.setModel(model)
        treeView.setRootIndex(model.index('C:/'))
        self.viewLayout.addWidget(treeView)

        tableView = BrowserTableView()
        tableView.setModel(model)
        tableView.setRootIndex(model.index('C:/'))
        tableView.setSelectionModel(treeView.selectionModel())
        self.viewLayout.addWidget(tableView)
        self.viewLayout.setCurrentIndex(1)

        self.treeViewButton.clicked.connect(self.switchToTreeView)
        self.addAction(createAction(self, 'Tree View', self.switchToTreeView, shortcut='Ctrl+1'))
        self.tableViewButton.clicked.connect(self.switchToTableView)
        self.addAction(createAction(self, 'Table View', self.switchToTableView, shortcut='Ctrl+2'))

        bottomLayout = QHBoxLayout()
        bottomLayout.setContentsMargins(4, 0, 4, 4)
        bottomLayout.setSpacing(2)

        settingsButton = QPushButton()
        settingsButton.setFixedSize(26, 26)
        settingsButton.setToolTip('Settings')
        settingsButton.setIcon(hou.qt.Icon('BUTTONS_gear_mini', 18, 18))
        settingsButton.setIconSize(QSize(18, 18))
        bottomLayout.addWidget(settingsButton)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        bottomLayout.addSpacerItem(spacer)

        self.scaleSlider = Slider()
        self.scaleSlider.setDefaultValue(50)
        self.scaleSlider.setFixedWidth(120)
        self.scaleSlider.valueChanged.connect(lambda v: tableView.setIconSize(QSize(120, 90) * v / 100))
        bottomLayout.addWidget(self.scaleSlider)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(4)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(middleLayout)
        mainLayout.addLayout(bottomLayout)

    def switchToTreeView(self):
        self.viewLayout.setCurrentIndex(0)
        self.scaleSlider.hide()
        self.treeViewButton.setChecked(True)

    def switchToTableView(self):
        self.viewLayout.setCurrentIndex(1)
        self.scaleSlider.show()
        self.tableViewButton.setChecked(True)

    def keyPressEvent(self, event):
        if False:  # Type hint
            event = QKeyEvent
        key = event.key()
        mod = event.modifiers()
        if mod == Qt.NoModifier and key == Qt.Key_F5:
            pass
        elif mod == Qt.ControlModifier and key == Qt.Key_F:
            self.searchField.setFocus()
        elif mod == Qt.NoModifier and key == Qt.Key_F3:
            self.searchField.setFocus()
        elif mod == Qt.ControlModifier and key == Qt.Key_Equal:
            pass
        elif mod == Qt.ControlModifier and key == Qt.Key_Minus:
            pass
        elif mod == Qt.ControlModifier and key == Qt.Key_1:
            pass
        elif mod == Qt.ControlModifier and key == Qt.Key_2:
            pass
        elif mod == Qt.NoModifier and key == Qt.Key_F1:
            pass
        else:
            super(ContentBrowser, self).keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = ContentBrowser()
    window.show()
    app.exec_()
