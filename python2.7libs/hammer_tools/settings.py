from __future__ import print_function

import json
import os

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

from .utils import clearLayout

DEFAULT_SETTINGS = {
    'hammer.previous_files.enable': True,
    'hammer.previous_files.startup': True,
    'hammer.previous_files.check_file_existence': True,
    'hammer.previous_files.db_location': '$HOUDINI_USER_PREF_DIR',
    'hammer.previous_files.silent.manual_update': True,
    'hammer.previous_files.silent.disable_sims': False,

    'hammer.parms.open_folder.enable': True,
    'hammer.parms.open_folder.use_custom_explorer': False,
    'hammer.parms.open_folder.custom_explorer_path': '',

    'hammer.nodes.play_sound.enable': True,
    'hammer.nodes.play_sound.use_external_player': True
}


class SettingsManager:
    _instance = None

    class State:
        Direct = 1
        Accumulation = 2

    class SaveBehaviour:
        Immediatly = 1
        OnDemand = 2

    def __init__(self, settings_file=None):
        # File
        if settings_file is None:
            self.__settings_file = hou.homeHoudiniDirectory() + '/hammer_tools.settings'
        elif os.path.isfile(settings_file):
            self.__settings_file = settings_file
        else:
            raise FileNotFoundError

        # Data
        self.__data = {}
        self.__accumulated_data = {}
        self.__state = SettingsManager.State.Direct
        self.__save_mode = SettingsManager.SaveBehaviour.Immediatly

        # Fill Data
        self.resetToFactoryDefaults()
        self.load()

    def beginEdit(self):
        self.__state = SettingsManager.State.Accumulation

    def endEdit(self, cancel=False):
        if self.__state == SettingsManager.State.Accumulation:
            return  # todo?: raise exception
        self.__state = SettingsManager.State.Direct
        if cancel:
            self.__accumulated_data.clear()
            return
        self.__data.update(self.__accumulated_data)
        self.__accumulated_data.clear()
        if self.__save_mode == SettingsManager.SaveBehaviour.Immediatly:
            self.save()

    def value(self, setting_key):
        if setting_key not in self.__data:
            raise ValueError('Invalid setting key')
        return self.__data[setting_key]

    def setValue(self, setting_key, value, force_direct=False):
        if self.__state == SettingsManager.State.Direct or force_direct:
            self.__data[setting_key] = value
            if self.__save_mode == SettingsManager.SaveBehaviour.Immediatly:
                self.save()
        elif self.__state == SettingsManager.State.Accumulation:
            self.__accumulated_data[setting_key] = value

    def save(self, settings_file=None):
        with open(self.__settings_file if settings_file is None else settings_file, 'w') as file:
            json.dump(self.__data, file, indent=4)

    def resetToFactoryDefaults(self):
        self.__data = DEFAULT_SETTINGS

    def load(self, settings_file=None, update=True):
        try:
            with open(self.__settings_file if settings_file is None else settings_file, 'r') as file:
                try:
                    data = json.load(file)
                    if update:
                        self.__data.update(data)
                    else:
                        self.__data = data
                except ValueError:
                    pass
        except IOError:
            pass

    def isSynced(self):
        raise NotImplementedError

    def sync(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


settings = SettingsManager.instance()


class AbstractSetting(QWidget):
    # Signals
    changed = Signal(object)

    def __init__(self, layout_orientation=Qt.Horizontal):
        super(AbstractSetting, self).__init__()

        # Layout
        if layout_orientation == Qt.Horizontal:
            main_layout = QHBoxLayout(self)
        else:
            main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

    def name(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    def key(self):
        raise NotImplementedError

    def value(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def notify(self):
        self.changed.emit(self)

    def __contains__(self, text):
        return text.lower() in self.name().lower() or \
               text.lower() in self.description().lower()

    def __str__(self):
        return 'Name - "{}"; ID - "{}"'.format(self.name(), self.key())


class ToggleSetting(AbstractSetting):
    def __init__(self, name, key, description=''):
        super(ToggleSetting, self).__init__()

        # Data
        self.__name = name
        self.__description = description
        self.__key = key

        # UI
        self.toggle = QCheckBox(self.name())
        self.toggle.stateChanged.connect(self.notify)
        self.layout().addWidget(self.toggle)

    def name(self):
        return self.__name

    def description(self):
        return self.__description

    def key(self):
        return self.__key

    def value(self):
        return self.toggle.isChecked()

    def setValue(self, value):
        self.toggle.setChecked(value)
        self.notify()


class PathSetting(AbstractSetting):
    def __init__(self, name, key, path_type, description=''):
        super(PathSetting, self).__init__()

        # Data
        self.__name = name
        self.__description = description
        self.__key = key
        self.__path_type = path_type

        # UI
        label = QLabel(self.name())
        label.setToolTip(self.description())
        self.layout().addWidget(label)

        self.path_edit = QLineEdit(self.name())
        self.path_edit.textChanged.connect(self.notify)
        self.layout().addWidget(self.path_edit)

        change_path_button = QPushButton('Change')
        change_path_button.clicked.connect(self.changePath)
        self.layout().addWidget(change_path_button)

    def changePath(self):
        if self.__path_type == 'folder':
            path = QFileDialog.getExistingDirectory(self.parentWidget(), self.__name)
        else:
            path, _ = QFileDialog.getOpenFileName(self.parentWidget(), self.__name)
        if path:
            self.setValue(path)

    def name(self):
        return self.__name

    def description(self):
        return self.__description

    def key(self):
        return self.__key

    def value(self):
        return self.path_edit.text()

    def setValue(self, value):
        self.path_edit.setText(value)
        self.notify()


class SettingGroup(QGroupBox):
    def __init__(self, name, toggle_setting=None, orientation=Qt.Vertical):
        super(SettingGroup, self).__init__()

        self.__toggle_setting = toggle_setting
        if toggle_setting is not None:
            self.setCheckable(True)
            self.setChecked(toggle_setting.value())
            self.toggled.connect(self.__toggle_setting.setValue)

        # Data
        self.__name = None
        self.setTitle(name)
        self.__settings = []

        # Layout
        if orientation == Qt.Vertical:
            main_layout = QVBoxLayout(self)
        else:
            main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

    def settings(self):
        return tuple(self.__settings)

    def addSetting(self, setting):
        self.__settings.append(setting)
        self.layout().addWidget(setting)

    def __contains__(self, text):
        for setting in self.settings():
            if text in setting:
                return True
        return False


class Section(QWidget):
    def __init__(self, name, description=''):
        super(Section, self).__init__()

        # Data
        self.__name = name
        self.__description = description
        self.__items = []

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def description(self):
        return self.__description

    def setDescription(self, text):
        self.__description = text

    def items(self):
        return self.__items

    def addItem(self, widget):
        self.__items.append(widget)
        self.layout().addWidget(widget)

    def __contains__(self, text):
        for item in self.items():
            if text in item:
                return True
        return False


SETTINGS_SCHEME = {
    'sections': [
        {
            'name': 'Previous Files',
            'settings': [
                {
                    'name': 'Enable',
                    'type': 'toggle',
                    'key': 'hammer.previous_files.enable'
                },
                {
                    'name': 'Launch on Startup',
                    'type': 'toggle',
                    'key': 'hammer.previous_files.startup'
                },
                {
                    'name': 'Check File Existence',
                    'type': 'toggle',
                    'key': 'hammer.previous_files.check_file_existence'
                },
                {
                    'name': 'Silent Mode',
                    'type': 'group',
                    'settings': [
                        {
                            'name': 'Manual Update',
                            'type': 'toggle',
                            'key': 'hammer.previous_files.silent.manual_update'
                        },
                        {
                            'name': 'Disable Simulations',
                            'type': 'toggle',
                            'key': 'hammer.previous_files.silent.disable_sims'
                        }
                    ]
                },
                {
                    'name': 'Database Location',
                    'type': 'path',
                    'path_type': 'folder',
                    'key': 'hammer.previous_files.db_location'
                }
            ]
        },
        {
            'name': 'Misc',
            'settings': [
                {
                    'name': 'Open Folder',
                    'type': 'group',
                    'settings': [
                        {
                            'name': 'Enable',
                            'type': 'toggle',
                            'key': 'hammer.parms.open_folder.enable'
                        },
                        {
                            'name': 'Use Custom Explorer',
                            'type': 'toggle',
                            'key': 'hammer.parms.open_folder.use_custom_explorer'
                        },
                        {
                            'name': 'Explorer Path',
                            'type': 'path',
                            'path_type': 'file',
                            'key': 'hammer.parms.open_folder.custom_explorer_path'
                        }
                    ]
                },
                {
                    'name': 'Play Sound',
                    'type': 'group',
                    'settings': [
                        {
                            'name': 'Enable',
                            'type': 'toggle',
                            'key': 'hammer.nodes.play_sound.enable'
                        },
                        {
                            'name': 'Use External Player',
                            'type': 'toggle',
                            'key': 'hammer.nodes.play_sound.use_external_player'
                        }
                    ]
                }
            ]
        }
    ]
}


def changeSettingValue(setting):
    settings.setValue(setting.key(), setting.value())


def parseSetting(setting_data):
    new_item = None
    if setting_data['type'] == 'toggle':
        new_item = ToggleSetting(setting_data['name'], setting_data['key'])
        new_item.setValue(settings.value(setting_data['key']))
    elif setting_data['type'] == 'path':
        new_item = PathSetting(setting_data['name'], setting_data['key'], setting_data['path_type'])
        new_item.setValue(settings.value(setting_data['key']))
    if new_item is not None:
        new_item.changed.connect(changeSettingValue)
    return new_item


def parseScheme(scheme):
    sections = []
    sections_data = scheme['sections']
    for section_data in sections_data:
        new_section = Section(section_data['name'])
        settings_data = section_data['settings']
        for setting_data in settings_data:
            setting_type = setting_data['type']
            setting_name = setting_data['name']
            if setting_type == 'group':
                new_item = SettingGroup(setting_name)
                group_settings_data = setting_data['settings']
                for group_setting_data in group_settings_data:
                    new_group_item = parseSetting(group_setting_data)
                    new_item.addSetting(new_group_item)
            else:
                new_item = parseSetting(setting_data)
            new_section.addItem(new_item)
        sections.append(new_section)
    return sections


class SectionListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(SectionListModel, self).__init__(parent)

        # Data
        self.__sections = []

    def setSectionList(self, sections):
        self.beginResetModel()
        self.__sections = sections
        self.endResetModel()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent):
        return len(self.__sections)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__sections[index.row()].name()
        if role == Qt.UserRole:
            return self.__sections[index.row()]


class SectionListView(QListView):
    def __init__(self):
        super(SectionListView, self).__init__()

        self.setAlternatingRowColors(True)


class SectionView(QWidget):
    def __init__(self, section=None):
        super(SectionView, self).__init__()

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Data
        self.__section = section
        if self.__section is not None:
            main_layout.addWidget(self.__section)

    def setSection(self, section):
        self.__section = section

        clearLayout(self.layout())
        self.layout().addWidget(self.__section)

        # Spacer
        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.layout().addSpacerItem(spacer)


class HammerSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(HammerSettingsDialog, self).__init__(parent, Qt.Window)

        # UI
        self.setWindowTitle('Hammer Tools: Settings')
        self.setStyleSheet(hou.qt.styleSheet())
        self.resize(800, 500)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        left_widget = QWidget()
        left_widget.setMaximumWidth(160)
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Section View
        self.section_view = SectionView()
        splitter.addWidget(self.section_view)

        # Section List
        sections = parseScheme(SETTINGS_SCHEME)

        self.section_list_model = SectionListModel(self)
        self.section_list_model.setSectionList(sections)

        self.section_list_view = SectionListView()
        self.section_list_view.setModel(self.section_list_model)
        selectionModel = self.section_list_view.selectionModel()
        selectionModel.currentChanged.connect(self.setCurrentSection)
        left_layout.addWidget(self.section_list_view)

    def setCurrentSection(self, index):
        self.section_view.setSection(index.data(Qt.UserRole))
