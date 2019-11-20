from __future__ import print_function

import os
import sqlite3

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

from .quick_selection import FilterField, FuzzyFilterProxyModel


def createDatabase(filepath):
    db = sqlite3.connect(filepath)

    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS `folder` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`path` TEXT UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS `file` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`folder_id` INTEGER NOT NULL,'
                   '`name` TEXT NOT NULL,'
                   '`extension` TEXT NOT NULL);')
    cursor.execute('CREATE TABLE IF NOT EXISTS `log` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`file_id` INTEGER,'
                   '`event` INTEGER,'
                   '`timestamp` INTEGER);')
    db.commit()

    return db


class LogEvent:
    Load = 0
    Save = 1


class SessionWatcher:
    def __init__(self):
        # Database
        db_file = os.path.abspath(os.path.join(hou.homeHoudiniDirectory(), 'hammer_previous_files.db'))
        if not os.path.exists(db_file):
            self.db = createDatabase(db_file)
        else:
            self.db = sqlite3.connect(db_file)

    def logEvent(self, filepath, event):
        query = self.db.cursor()
        folder, fullname = os.path.split(filepath)
        name, extension = os.path.splitext(fullname)
        # Check folder and get id
        r = query.execute('SELECT `id` FROM `folder` WHERE `path` == ? LIMIT 1;', (folder,))
        r = r.fetchone()
        if r is None:
            query.execute('INSERT INTO `folder` (path) VALUES (?);', (folder,))
            self.db.commit()
            rowid = query.lastrowid
        else:
            rowid = r[0]
        # Check file and get id
        r = query.execute('SELECT `id` FROM `file` WHERE `folder_id` == ? AND `name` == ? AND `extension` == ? LIMIT 1;',
                          (rowid, name, extension))
        r = r.fetchone()
        if r is None:
            query.execute('INSERT INTO `file` (`folder_id`, `name`, `extension`) VALUES (?, ?, ?);',
                          (rowid, name, extension))
            self.db.commit()
            rowid = query.lastrowid
        else:
            rowid = r[0]
        # Add event to log
        query.execute('INSERT INTO `log` (`file_id`, `event`, `timestamp`) VALUES (?, ?, CURRENT_TIMESTAMP);',
                      (rowid, event))
        self.db.commit()

    def __call__(self, event_type):
        if event_type == hou.hipFileEventType.AfterLoad:
            self.logEvent(hou.hipFile.path(), LogEvent.Load)
        elif event_type == hou.hipFileEventType.BeforeSave:
            self.logEvent(hou.hipFile.path(), LogEvent.Save)


def setSessionWatcher():
    hou.session.__hammer_session_watcher = SessionWatcher()
    hou.hipFile.addEventCallback(hou.session.__hammer_session_watcher)


class PreviousFilesModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(PreviousFilesModel, self).__init__(parent)

        # Database
        db_file = os.path.abspath(os.path.join(hou.homeHoudiniDirectory(), 'hammer_previous_files.db'))
        if not os.path.exists(db_file):
            self.db = createDatabase(db_file)
        else:
            self.db = sqlite3.connect(db_file)

        self.log = (())

        self.updateLogData()

    def updateLogData(self):
        self.beginResetModel()
        self.log = self.db.cursor().execute('SELECT file.name, folder.path, log.timestamp, file.extension FROM `log` '
                                            'JOIN `file` ON log.file_id = file.id '
                                            'JOIN `folder` ON file.folder_id = folder.id '
                                            'GROUP BY log.file_id '
                                            'ORDER BY log.id DESC;').fetchall()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.log)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        headers = ('Name', 'Folder', 'Timestamp')
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.log[index.row()][index.column()]
        elif role == Qt.UserRole and index.column() == 0:
            return self.log[index.row()][3]


class PreviousFilesView(QTableView):
    def __init__(self):
        super(PreviousFilesView, self).__init__()

        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.doubleClicked.connect(self.openSelectedFile)

        refreshAction = QAction('Refresh', self)
        refreshAction.setShortcut(QKeySequence(Qt.Key_F5))
        refreshAction.triggered.connect(lambda: self.model().updateLogData())
        self.addAction(refreshAction)

        # Menu
        self.createMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

    def createMenu(self):
        menu = QMenu(self)

        self.openSelectedFileAction = QAction('Open', self)
        self.openSelectedFileAction.triggered.connect(self.openSelectedFile)
        menu.addAction(self.openSelectedFileAction)

        self.openSelectedFileInManualModeAction = QAction('Open in Manual Mode', self)
        self.openSelectedFileInManualModeAction.triggered.connect(self.openSelectedFileInManualMode)
        menu.addAction(self.openSelectedFileInManualModeAction)

        self.mergeSelectedFilesAction = QAction('Merge', self)
        self.mergeSelectedFilesAction.triggered.connect(self.mergeSelectedFiles)
        menu.addAction(self.mergeSelectedFilesAction)

        self.openSelectedFoldersAction = QAction('Open Folder', self)
        self.openSelectedFoldersAction.triggered.connect(self.openSelectedFolders)
        menu.addAction(self.openSelectedFoldersAction)

        self.menu = menu

    def showMenu(self):
        selectionModel = self.selectionModel()
        selectedRowCount = len(selectionModel.selectedRows())
        if selectedRowCount > 0:
            if selectedRowCount > 1:
                self.openSelectedFileAction.setEnabled(False)
                self.openSelectedFileInManualModeAction.setEnabled(False)
            else:
                self.openSelectedFileAction.setEnabled(True)
                self.openSelectedFileInManualModeAction.setEnabled(True)
            self.menu.exec_(QCursor.pos())

    def openSelectedFile(self):
        selection = self.selectionModel()
        name = selection.selectedRows(0)[0].data(Qt.DisplayRole)
        extension = selection.selectedRows(0)[0].data(Qt.UserRole)
        folder = selection.selectedRows(1)[0].data(Qt.DisplayRole)

        hou.hipFile.load('{}/{}{}'.format(folder, name, extension))

    def openSelectedFileInManualMode(self):
        self.openSelectedFile()
        hou.setUpdateMode(hou.updateMode.Manual)

    def mergeSelectedFiles(self):
        raise NotImplementedError

    def openSelectedFolders(self):
        selection = self.selectionModel()
        folder = selection.selectedRows(1)[0].data(Qt.DisplayRole)
        os.startfile(folder)


def openTemp():
    os.startfile(hou.getenv('TEMP'))


class PreviousFiles(QDialog):
    def __init__(self, parent=None):
        super(PreviousFiles, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Previous Files')
        self.resize(800, 500)
        self.setStyleSheet(hou.qt.styleSheet())

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(4)

        self.left_vertical_layout = QVBoxLayout()
        self.left_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.left_vertical_layout.setSpacing(0)
        self.main_layout.addLayout(self.left_vertical_layout)

        self.new = QPushButton('New File')
        self.new.setMinimumWidth(100)
        self.new.clicked.connect(self.createNewHip)
        self.left_vertical_layout.addWidget(self.new)

        self.open_menu = QMenu(self)
        open_in_manual_mode = QAction('Open in Manual Mode', self)
        open_in_manual_mode.triggered.connect(lambda: self.openHip(True))
        self.open_menu.addAction(open_in_manual_mode)

        self.open = QToolButton()
        self.open.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open.setMenu(self.open_menu)
        self.open.setStyleSheet('border-radius: 1; border-style: none')
        self.open.setMinimumWidth(100)
        self.open.setText('Open...')
        self.open.clicked.connect(self.openHip)
        self.left_vertical_layout.addWidget(self.open)

        self.merge = QPushButton('Merge...')
        self.merge.clicked.connect(self.mergeHips)
        self.left_vertical_layout.addWidget(self.merge)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.left_vertical_layout.addSpacerItem(spacer)

        self.open_temp = QPushButton('Open Temp')
        self.open_temp.clicked.connect(openTemp)
        self.left_vertical_layout.addWidget(self.open_temp)

        self.open_crash = QPushButton('Open Crash')
        self.open_crash.clicked.connect(self.openLastCrashFile)
        self.left_vertical_layout.addWidget(self.open_crash)

        self.right_vertical_layout = QVBoxLayout()
        self.right_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.right_vertical_layout.setSpacing(0)
        self.main_layout.addLayout(self.right_vertical_layout)

        # File list
        self.model = PreviousFilesModel(self)
        self.filter_model = FuzzyFilterProxyModel(self)
        self.filter_model.setSourceModel(self.model)
        self.view = PreviousFilesView()
        self.view.setModel(self.filter_model)

        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(self.filter_model.setFilterPattern)

        self.right_vertical_layout.addWidget(self.filter_field)
        self.right_vertical_layout.addWidget(self.view)

    def createNewHip(self):
        self.hide()
        hou.hipFile.clear()

    def openHip(self, manual=False):
        files = hou.ui.selectFile(title='Open', file_type=hou.fileType.Hip, chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            hou.hipFile.load(files[0])
            self.hide()
            if manual:
                hou.setUpdateMode(hou.updateMode.Manual)

    def mergeHips(self):
        files = hou.ui.selectFile(title='Merge', file_type=hou.fileType.Hip, multiple_select=True, chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            for file in tuple(map(lambda f: hou.expandString(f), files)):
                hou.hipFile.merge(file)
            self.hide()

    def detectCrashFile(self):
        temp_path = hou.getenv('TEMP')
        for file in os.listdir(temp_path):
            if file.startswith('crash.') and file.endswith('.hip') or file.endswith('.hiplc') or file.endswith('.hipnc'):
                self.open_crash.setVisible(True)
                return
        self.open_crash.setVisible(False)

    def openLastCrashFile(self, manual=False):
        last_file = None
        last_timestamp = 0
        houdini_temp_path = hou.getenv('TEMP')
        for file in os.listdir(houdini_temp_path):
            if file.startswith('crash.') and file.endswith('.hip') or file.endswith('.hiplc') or file.endswith('.hipnc'):
                timestamp = os.stat('{}/{}'.format(houdini_temp_path, file)).st_mtime
                if timestamp > last_timestamp:
                    last_timestamp = timestamp
                    last_file = file
        if last_file is None:
            hou.ui.displayMessage('Crash file not found')
            self.detectCrashFile()
        else:
            self.hide()
            hou.hipFile.load('{}/{}'.format(houdini_temp_path, last_file))
            if manual:
                hou.setUpdateMode(hou.updateMode.Manual)

    def showEvent(self, event):
        self.detectCrashFile()
        super(PreviousFiles, self).showEvent(event)


def show():
    if not hasattr(hou.session, 'hammer_previous_files'):
        hou.session.hammer_previous_files = PreviousFiles(hou.qt.mainWindow())
    hou.session.hammer_previous_files.show()
