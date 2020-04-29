from __future__ import print_function

import os
import sqlite3
import subprocess

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

from .quick_selection import FilterField
from .utils import fuzzyMatch, openLocation
from .settings import SettingsManager

settings = SettingsManager.instance()


def importRecentFiles(watcher):
    try:
        with open(os.path.join(hou.homeHoudiniDirectory(), 'file.history')) as file:
            on_hip = False
            in_block = False
            for line in file:
                if not on_hip and not in_block and line.startswith('HIP'):
                    on_hip = True
                elif on_hip:
                    on_hip = False
                    in_block = True
                elif in_block and not line.startswith('}'):
                    path = hou.expandString(line.strip(' \n'))
                    watcher.logEvent(path, SessionWatcher.EventType.Save)
                else:
                    in_block = False
    except IOError:
        pass


def importFromPreviousVersion(watcher):
    import sys
    import re

    DOC_PATH = os.path.dirname(hou.expandString('$HOUDINI_USER_PREF_DIR'))

    houdini_folders = []
    for item in os.listdir(DOC_PATH):
        if re.match('houdini\d*\.\d*', item) and os.path.isdir(os.path.join(DOC_PATH, item)):
            houdini_folders.append(item)
    houdini_folders = tuple(reversed(sorted(houdini_folders)))

    current_houdini_folder = os.path.basename(hou.getenv('HOUDINI_USER_PREF_DIR'))
    try:
        index = houdini_folders.index(current_houdini_folder)
        houdini_folders = houdini_folders[index + 1:]
        prev_houdini_folder = houdini_folders[0]
    except ValueError:  # Non-default HOUDINI_USER_PREF_DIR
        return
    except IndexError:  # No previous Houdini folders found
        return

    prev_db_file_path = os.path.join(DOC_PATH, prev_houdini_folder, 'hammer_previous_files.db')
    if not os.path.exists(prev_db_file_path):
        return

    prev_db = sqlite3.connect(prev_db_file_path)
    prev_log = prev_db.cursor().execute('SELECT (folder.path || "/" || file.name || file.extension),'
                                        ' log.event, log.timestamp FROM `log` '
                                        'JOIN `file` ON log.file_id = file.id '
                                        'JOIN `folder` ON file.folder_id = folder.id '
                                        'GROUP BY log.file_id '
                                        'ORDER BY log.id DESC;').fetchall()

    for file_path, event, timestamp in prev_log:
        watcher.logEvent(path, event, timestamp)


def createDatabase(filepath):
    db = sqlite3.connect(filepath)

    cursor = db.cursor()
    cursor.execute('CREATE TABLE `folder` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`path` TEXT UNIQUE);')
    cursor.execute('CREATE TABLE `file` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`folder_id` INTEGER NOT NULL,'
                   '`name` TEXT NOT NULL,'
                   '`extension` TEXT NOT NULL);')
    cursor.execute('CREATE TABLE `log` ('
                   '`id` INTEGER PRIMARY KEY,'
                   '`file_id` INTEGER,'
                   '`event` INTEGER,'
                   '`timestamp` INTEGER);')
    db.commit()

    return db


class SessionWatcher:
    class EventType:
        Load = 0
        Save = 1

    def __init__(self):
        # Database
        db_file = os.path.abspath(os.path.join(hou.expandString(settings.value('hammer.previous_files.db_location')),
                                               'hammer_previous_files.db'))
        if not os.path.exists(db_file):
            self.db = createDatabase(db_file)
        else:
            self.db = sqlite3.connect(db_file)

        # First Start
        if settings.value('hammer.previous_files.first_start'):
            # noinspection PyTypeChecker
            reply = QMessageBox.question(None, 'Hammer: Previous Files',
                                         'Import database from previous Houdini version?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                importFromPreviousVersion(self)

            # noinspection PyTypeChecker
            reply = QMessageBox.question(None, 'Hammer: Previous Files',
                                         'Import recent files?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                importRecentFiles(self)

            settings.setValue('hammer.previous_files.first_start', False)

    def logEvent(self, filepath, event, timestamp=None):
        query = self.db.cursor()
        location, fullname = os.path.split(filepath)
        name, extension = os.path.splitext(fullname)
        # Check folder and get id
        r = query.execute('SELECT `id` FROM `folder` WHERE `path` == ? LIMIT 1;', (location,))
        r = r.fetchone()
        if r is None:
            query.execute('INSERT INTO `folder` (`path`) VALUES (?);', (location,))
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
        if timestamp:
            query.execute('INSERT INTO `log` (`file_id`, `event`, `timestamp`) VALUES (?, ?, ?);',
                          (rowid, event, timestamp))
        else:
            query.execute('INSERT INTO `log` (`file_id`, `event`, `timestamp`) VALUES (?, ?, datetime("now", "localtime"));',
                          (rowid, event))
        self.db.commit()

    def __call__(self, event_type):
        if event_type == hou.hipFileEventType.AfterLoad:
            self.logEvent(hou.hipFile.path(), SessionWatcher.EventType.Load)
        elif event_type == hou.hipFileEventType.BeforeSave:
            self.logEvent(hou.hipFile.path(), SessionWatcher.EventType.Save)


def setSessionWatcher():
    if not settings.value('hammer.previous_files.enable'):
        return
    if not hasattr(hou.session, 'hammer_session_watcher'):
        hou.session.hammer_session_watcher = SessionWatcher()
        hou.hipFile.addEventCallback(hou.session.hammer_session_watcher)


class FuzzyFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FuzzyFilterProxyModel, self).__init__(parent)

        self.__filter_pattern = ''
        self.setDynamicSortFilter(True)

    def setFilterPattern(self, pattern):
        self.beginResetModel()
        if self.filterCaseSensitivity() == Qt.CaseInsensitive:
            self.__filter_pattern = pattern.lower()
        else:
            self.__filter_pattern = pattern
        self.endResetModel()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        text = source_model.data(source_model.index(source_row, 1, source_parent), Qt.UserRole)
        matches, weight = fuzzyMatch(self.__filter_pattern, text if self.filterCaseSensitivity() == Qt.CaseSensitive else text.lower())
        return matches

    def lessThan(self, source_left, source_right):
        text1 = source_left.data(Qt.DisplayRole)
        _, weight1 = fuzzyMatch(self.__filter_pattern, text1 if self.filterCaseSensitivity() == Qt.CaseSensitive else text1.lower())

        text2 = source_right.data(Qt.DisplayRole)
        _, weight2 = fuzzyMatch(self.__filter_pattern, text2 if self.filterCaseSensitivity() == Qt.CaseSensitive else text2.lower())

        return weight1 < weight2


class PreviousFilesModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(PreviousFilesModel, self).__init__(parent)

        # Icons
        self.__file_exists_icon = hou.qt.Icon('TOP_status_cooked', 20, 20)
        self.__file_not_exists_icon = hou.qt.Icon('TOP_status_error', 20, 20)

        # Database
        db_file = os.path.abspath(os.path.join(hou.expandString(settings.value('hammer.previous_files.db_location')),
                                               'hammer_previous_files.db'))
        if not os.path.exists(db_file):
            self.db = createDatabase(db_file)
        else:
            self.db = sqlite3.connect(db_file)

        self.__log = (())

        self.updateLogData()

    def updateLogData(self):
        self.beginResetModel()
        self.__log = self.db.cursor().execute('SELECT file.name, folder.path, log.timestamp, file.extension FROM `log` '
                                              'JOIN `file` ON log.file_id = file.id '
                                              'JOIN `folder` ON file.folder_id = folder.id '
                                              'GROUP BY log.file_id '
                                              'ORDER BY log.id DESC;').fetchall()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__log)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        headers = ('Name', 'Location', 'Timestamp')
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.__log[index.row()][0] + self.__log[index.row()][3]
            else:
                return self.__log[index.row()][index.column()]
        elif role == Qt.UserRole:
            if index.column() == 1:
                row = index.row()
                name, location, _, extension = self.__log[row]
                return os.path.normpath(os.path.join(location, name + extension)).replace('\\', '/')
        elif role == Qt.DecorationRole:
            if index.column() == 0 and settings.value('hammer.previous_files.check_file_existence'):
                name, location, _, extension = self.__log[index.row()]
                if os.path.exists(os.path.join(location, name + extension)):
                    return self.__file_exists_icon
                else:
                    return self.__file_not_exists_icon


class PreviousFilesView(QTableView):
    # Signals
    accepted = Signal()

    def __init__(self):
        super(PreviousFilesView, self).__init__()

        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit()
        else:
            super(PreviousFilesView, self).keyPressEvent(event)


def openTemp():
    os.startfile(hou.getenv('TEMP'))


def importFilmboxScene(path, suppress_save_prompt=False):
    hou.hipFile.importFBX(file_name=path, suppress_save_prompt=suppress_save_prompt,
                          override_scene_frame_range=True, unlock_geometry=True,
                          unlock_deformations=True, import_into_object_subnet=False,
                          convert_into_y_up_coordinate_system=True)


def importAlembicScene(path):
    location, file = os.path.split(path)
    name, extension = os.path.splitext(file)
    obj_node = hou.node('/obj')
    alembic_node = obj_node.createNode('alembicarchive', name)
    alembic_node.parm('fileName').set(path)
    alembic_node.parm('buildHierarchy').pressButton()


def importGLTFScene(path):
    location, file = os.path.split(path)
    name, extension = os.path.splitext(file)
    obj_node = hou.node('/obj')
    gltf_node = obj_node.createNode('gltf_hierarchy', name)
    gltf_node.parm('filename').set(path)
    gltf_node.parm('lockgeo').set(0)
    if extension.lower() == '.glb':
        gltf_node.parm('assetfolder').set('$HIP/{}_data'.format(name))
    gltf_node.parm('buildscene').pressButton()


def switchToSilentMode():
    if settings.value('hammer.previous_files.silent.manual_update'):
        hou.setUpdateMode(hou.updateMode.Manual)
    if settings.value('hammer.previous_files.silent.disable_sims'):
        hou.setSimulationEnabled(False)


class PreviousFiles(QDialog):
    def __init__(self, parent=None):
        super(PreviousFiles, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Previous Files')
        self.resize(800, 500)
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        left_vertical_layout = QVBoxLayout()
        left_vertical_layout.setContentsMargins(0, 0, 0, 0)
        left_vertical_layout.setSpacing(0)
        main_layout.addLayout(left_vertical_layout)

        self.new_button = QPushButton('New File')
        self.new_button.setMinimumWidth(100)
        self.new_button.clicked.connect(self.createNewHip)
        left_vertical_layout.addWidget(self.new_button)

        self.open_button_menu = QMenu(self)
        open_silently = QAction('Open Silently', self)
        open_silently.triggered.connect(lambda: self.chooseAndOpenFile(True))
        self.open_button_menu.addAction(open_silently)

        self.open_button = QToolButton()
        self.open_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_button.setMenu(self.open_button_menu)
        self.open_button.setStyleSheet('border-radius: 1; border-style: none')
        self.open_button.setMinimumWidth(100)
        self.open_button.setText('Open...')
        self.open_button.clicked.connect(self.chooseAndOpenFile)
        left_vertical_layout.addWidget(self.open_button)

        self.merge_button = QPushButton('Merge...')
        self.merge_button.clicked.connect(self.mergeFiles)
        left_vertical_layout.addWidget(self.merge_button)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        left_vertical_layout.addSpacerItem(spacer)

        self.open_temp_button = QPushButton('Open Temp')
        self.open_temp_button.setToolTip('Open Houdini Temp Location')
        self.open_temp_button.clicked.connect(openTemp)
        left_vertical_layout.addWidget(self.open_temp_button)

        # Crash menu
        self.open_crash_button_menu = QMenu(self)

        open_crash_silently = QAction('Open Silently', self)
        open_crash_silently.triggered.connect(lambda: self.openLastCrashFile(True))
        self.open_crash_button_menu.addAction(open_crash_silently)

        delete_crash_files = QAction('Delete all Crash Files', self)
        delete_crash_files.triggered.connect(self.deleteAllCrashFiles)
        self.open_crash_button_menu.addAction(delete_crash_files)

        self.open_crash_button = QToolButton()
        self.open_crash_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_crash_button.setMenu(self.open_crash_button_menu)
        self.open_crash_button.setStyleSheet('border-radius: 1; border-style: none;'
                                             'background-color: rgb(165, 70, 70);')
        self.open_crash_button.setMinimumWidth(100)
        self.open_crash_button.setText('Open Crash')
        self.open_crash_button.setToolTip('Open Last Crash File')
        self.open_crash_button.clicked.connect(self.openLastCrashFile)
        left_vertical_layout.addWidget(self.open_crash_button)

        right_vertical_layout = QVBoxLayout()
        right_vertical_layout.setContentsMargins(0, 0, 0, 0)
        right_vertical_layout.setSpacing(0)
        main_layout.addLayout(right_vertical_layout)

        # Filter
        self.filter_field = FilterField()
        right_vertical_layout.addWidget(self.filter_field)

        # File list
        self.model = PreviousFilesModel(self)

        self.filter_model = FuzzyFilterProxyModel(self)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.setSourceModel(self.model)

        self.view = PreviousFilesView()
        self.view.setModel(self.filter_model)
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, Qt.DescendingOrder)
        self.view.doubleClicked.connect(lambda: self.openSelectedFile())
        right_vertical_layout.addWidget(self.view)
        self.view.accepted.connect(lambda: self.openSelectedFile())

        self.filter_field.accepted.connect(self.openFirstFile)
        self.filter_field.downPressed.connect(self.switchToList)
        self.filter_field.textChanged.connect(self.filter_model.setFilterPattern)

        # File list menu
        self.menu = QMenu()
        self.menu.setStyleSheet(hou.qt.styleSheet())

        self.open_selected_file_action = QAction('Open', self)
        self.open_selected_file_action.triggered.connect(lambda: self.openSelectedFile())
        self.menu.addAction(self.open_selected_file_action)

        self.open_selected_file_silently_action = QAction('Open Silently', self)
        self.open_selected_file_silently_action.triggered.connect(lambda: self.openSelectedFile(True))
        self.menu.addAction(self.open_selected_file_silently_action)

        self.open_new_session_action = QAction('Open in New Session', self)
        self.open_new_session_action.triggered.connect(lambda: self.openSelectedFileInNewSession())
        self.menu.addAction(self.open_new_session_action)

        self.open_new_session_silently_action = QAction('Open in New Session Silently', self)
        self.open_new_session_silently_action.triggered.connect(lambda: self.openSelectedFileInNewSession(True))
        self.menu.addAction(self.open_new_session_silently_action)

        self.merge_selected_files_action = QAction('Merge', self)
        self.merge_selected_files_action.triggered.connect(self.mergeSelectedFiles)
        self.menu.addAction(self.merge_selected_files_action)

        self.open_selected_locations_action = QAction('Open Location', self)
        self.open_selected_locations_action.triggered.connect(self.openSelectedLocations)
        self.menu.addAction(self.open_selected_locations_action)

        self.menu.addSeparator()

        self.filter_by_name_action = QAction('Filter by Name', self)
        self.filter_by_name_action.triggered.connect(self.filterByName)
        self.menu.addAction(self.filter_by_name_action)

        self.filter_by_extension_action = QAction('Filter by Extension', self)
        self.filter_by_extension_action.triggered.connect(self.filterByExtension)
        self.menu.addAction(self.filter_by_extension_action)

        self.filter_by_location_action = QAction('Filter by Location', self)
        self.filter_by_location_action.triggered.connect(self.filterByLocation)
        self.menu.addAction(self.filter_by_location_action)

        self.menu.addSeparator()

        self.copy_name_action = QAction('Copy Name', self)
        self.copy_name_action.triggered.connect(self.copySelectedNames)
        self.menu.addAction(self.copy_name_action)

        self.copy_location_action = QAction('Copy Location', self)
        self.copy_location_action.triggered.connect(self.copySelectedLocations)
        self.menu.addAction(self.copy_location_action)

        self.copy_link_action = QAction('Copy Link', self)
        self.copy_link_action.triggered.connect(self.copySelectedLinks)
        self.menu.addAction(self.copy_link_action)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.showMenu)

        # Actions
        refresh_action = QAction('Refresh', self)
        refresh_action.setShortcut(QKeySequence(Qt.Key_F5))
        refresh_action.triggered.connect(self.model.updateLogData)
        self.addAction(refresh_action)

    def switchToList(self):
        self.view.setFocus()
        selection = self.view.selectionModel()
        selection.select(self.filter_model.index(0, 0), QItemSelectionModel.ClearAndSelect)
        selection.select(self.filter_model.index(0, 1), QItemSelectionModel.Select)
        selection.select(self.filter_model.index(0, 2), QItemSelectionModel.Select)

    def showMenu(self):
        selection = self.view.selectionModel()
        selected_row_count = len(selection.selectedRows())
        if selected_row_count > 0:
            if selected_row_count > 1:
                self.open_selected_file_action.setEnabled(False)
                self.open_selected_file_silently_action.setEnabled(False)
                self.filter_by_name_action.setEnabled(False)
                self.filter_by_extension_action.setEnabled(False)
                self.filter_by_location_action.setEnabled(False)
            else:  # Single file
                self.open_selected_file_action.setEnabled(True)
                self.open_selected_file_silently_action.setEnabled(True)
                self.filter_by_name_action.setEnabled(True)
                self.filter_by_extension_action.setEnabled(True)
                self.filter_by_location_action.setEnabled(True)
            self.menu.exec_(QCursor.pos())

    def openSelectedFile(self, silent=False):
        self.hide()
        selection = self.view.selectionModel()
        location = selection.selectedRows(1)[0].data(Qt.DisplayRole)
        name = selection.selectedRows(0)[0].data(Qt.DisplayRole)
        self.openFile('{}/{}'.format(location, name), silent)

    def openFirstFile(self):
        selection = self.view.selectionModel()
        selection.select(self.filter_model.index(0, 0), QItemSelectionModel.ClearAndSelect)
        selection.select(self.filter_model.index(0, 1), QItemSelectionModel.Select)
        selection.select(self.filter_model.index(0, 2), QItemSelectionModel.Select)
        self.openSelectedFile()

    def openSelectedFileInNewSession(self, silent=False):
        selection = self.view.selectionModel()
        location = selection.selectedRows(1)[0].data(Qt.DisplayRole)
        name = selection.selectedRows(0)[0].data(Qt.DisplayRole)
        cmd = ''
        cmd += '{}'.format(hou.expandString('$HFS/bin/houdini'))
        if silent:
            cmd += ' -n'
        cmd += ' {}/{}'.format(location, name)
        subprocess.Popen(cmd)

    def mergeSelectedFiles(self):
        self.hide()
        selection = self.view.selectionModel()
        locations = (index.data(Qt.DisplayRole) for index in selection.selectedRows(1))
        names = (index.data(Qt.DisplayRole) for index in selection.selectedRows(0))
        for location, name in zip(locations, names):
            hou.hipFile.merge('{}/{}'.format(location, name))

    def openSelectedLocations(self):
        selection = self.view.selectionModel()
        if len(selection.selectedRows()) > 4:
            return
        for index in selection.selectedRows(1):
            openLocation(index.data(Qt.DisplayRole))

    def createNewHip(self):
        self.hide()
        hou.hipFile.clear()

    def openFile(self, file, silent=False):
        file = hou.expandString(file)
        _, extension = os.path.splitext(file)
        try:
            if extension.lower().startswith('.hip'):
                hou.hipFile.load(file)
            else:
                hou.hipFile.clear(suppress_save_prompt=True)
                if extension.lower() == '.abc':
                    importAlembicScene(file)
                elif extension.lower() == '.fbx':
                    importFilmboxScene(file)
                elif extension.lower().startswith('.gl'):
                    importGLTFScene(file)
                hou.session.hammer_session_watcher.logEvent(file, SessionWatcher.EventType.Load)
            if silent:
                switchToSilentMode()
            self.hide()
        except hou.OperationFailed:
            self.show()

    def chooseAndOpenFile(self, silent=False):
        files = hou.ui.selectFile(title='Open', pattern='*.hip, *.hipnc, *.hiplc, *.hip*, *.abc, *.fbx, *.gltf, *.glb', chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            self.openFile(files[0], silent)

    def mergeFiles(self):
        files = hou.ui.selectFile(title='Merge', file_type=hou.fileType.Hip, multiple_select=True, chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            files = [hou.expandString(file) for file in files]  # Prevent aging variables
            for file in files:
                hou.hipFile.merge(file)
            self.hide()

    def detectCrashFile(self):
        temp_path = hou.getenv('TEMP')
        for file in os.listdir(temp_path):
            if file.startswith('crash.') and file.endswith('.hip') or file.endswith('.hiplc') or file.endswith('.hipnc'):
                self.open_crash_button.setVisible(True)
                return
        self.open_crash_button.setVisible(False)

    def openLastCrashFile(self, silent=False):
        last_file = None
        last_timestamp = 0
        houdini_temp_path = hou.getenv('TEMP')
        for file in os.listdir(houdini_temp_path):
            name, extension = os.path.splitext(file)
            if name.startswith('crash.') and extension.startswith('.hip'):
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
            if silent:
                switchToSilentMode()

    def deleteAllCrashFiles(self):
        houdini_temp_path = hou.getenv('TEMP')
        for file in os.listdir(houdini_temp_path):
            name, extension = os.path.splitext(file)
            if name.startswith('crash.') and extension.startswith('.hip'):
                os.remove(os.path.join(houdini_temp_path, file))
        self.detectCrashFile()

    def filterByName(self):
        selection = self.view.selectionModel()
        name = os.path.splitext(selection.selectedRows(0)[0].data(Qt.DisplayRole))[0]
        self.filter_field.setText(name)

    def filterByExtension(self):
        selection = self.view.selectionModel()
        extension = os.path.splitext(selection.selectedRows(0)[0].data(Qt.DisplayRole))[1]
        self.filter_field.setText(extension)

    def filterByLocation(self):
        selection = self.view.selectionModel()
        location = selection.selectedRows(1)[0].data(Qt.DisplayRole)
        self.filter_field.setText(location)

    def copySelectedNames(self):
        selection = self.view.selectionModel()
        names = []
        for index in selection.selectedRows(0):
            names.append(index.data(Qt.DisplayRole))
        qApp.clipboard().setText('\n'.join(names))

    def copySelectedLocations(self):
        selection = self.view.selectionModel()
        locations = []
        for index in selection.selectedRows(1):
            locations.append(index.data(Qt.DisplayRole))
        qApp.clipboard().setText('\n'.join(locations))

    def copySelectedLinks(self):
        selection = self.view.selectionModel()
        links = []
        for index in selection.selectedRows(1):
            links.append(index.data(Qt.UserRole))
        qApp.clipboard().setText('\n'.join(links))

    def showEvent(self, event):
        self.model.updateLogData()
        self.detectCrashFile()
        self.filter_field.setFocus()
        self.filter_field.selectAll()
        super(PreviousFiles, self).showEvent(event)


def showPreviousFiles():
    if not settings.value('hammer.previous_files.enable'):
        return
    if not hasattr(hou.session, 'hammer_previous_files'):
        hou.session.hammer_previous_files = PreviousFiles(hou.qt.mainWindow())
    hou.session.hammer_previous_files.show()
