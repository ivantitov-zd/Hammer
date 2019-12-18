from __future__ import print_function

import json

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


class SettingsManager:
    class State:
        Direct = 1
        Accumulation = 2

    class SaveBehaviour:
        Immediatly = 1
        OnDemand = 2

    def __init__(self):
        self.pref_file = hou.homeHoudiniDirectory() + '/hammer_tools.pref'

        # Data
        self.__data = {}
        self.__accumulated_data = {}
        self.__state = SettingsManager.State.Direct
        self.__save_mode = SettingsManager.SaveBehaviour.Immediatly

    def beginEdit(self):
        self.__state = SettingsManager.State.Accumulation

    def endEdit(self):  # todo: autosync?
        self.__state = SettingsManager.State.Direct
        self.__data.update(self.__accumulated_data)
        self.__accumulated_data.clear()
        if self.__save_mode == SettingsManager.SaveBehaviour.Immediatly:
            self.save()

    def value(self, setting_id):
        if setting_id not in self.__data:
            raise Exception  # todo exception
        return self.__data[setting_id]

    def setValue(self, setting_id, value):
        if setting_id in self.__data:
            if self.__state == SettingsManager.State.Direct:
                self.__data[setting_id] = value
                if self.__save_mode == SettingsManager.SaveBehaviour.Immediatly:
                    self.save()
            elif self.__state == SettingsManager.State.Accumulation:
                self.__accumulated_data[setting_id] = value
            else:
                raise Exception  # todo exception
        # todo?: new id

    def save(self, path=None):
        # todo: try and state
        with open(self.pref_file if path is None else path, 'w') as file:
            json.dump(self.__data, file)

    def load(self, path=None):
        # todo: try and state
        with open(self.pref_file if path is None else path, 'r') as file:
            self.__data = json.load(file)

    def sync(self):
        raise NotImplementedError


class AbstractSetting(QWidget):
    # Signals
    changed = Signal(int)

    def __init__(self):
        super(AbstractSetting, self).__init__()

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

    def name(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    def id(self):
        raise NotImplementedError

    def value(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError


class SettingGroup(QGroupBox):
    def __init__(self, name):
        super(SettingGroup, self).__init__()

        # Data
        self.__name = None
        self.setName(name)

        # Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name
        self.setTitle(name)

    def addSetting(self, setting):
        self.layout().addWidget(setting)


class EnableOpenFolder(AbstractSetting):
    def __init__(self):
        super(EnableOpenFolder, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Open Folder'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_open_folder'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnablePreviousFiles(AbstractSetting):
    def __init__(self):
        super(EnablePreviousFiles, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Previous Files'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_previous_files'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnableSetInterpolation(AbstractSetting):
    def __init__(self):
        super(EnableSetInterpolation, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Set Interpolation'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_set_interpolation'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnablePlaySound(AbstractSetting):
    def __init__(self):
        super(EnablePlaySound, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Play Sound'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_play_sound'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnableSetSceneAudio(AbstractSetting):
    def __init__(self):
        super(EnableSetSceneAudio, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Play as Scene Audio'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_play_as_scene_audio'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnableQuickSelection(AbstractSetting):
    def __init__(self):
        super(EnableQuickSelection, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Quick Selection'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_quick_selection'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnableCollectFiles(AbstractSetting):
    def __init__(self):
        super(EnableCollectFiles, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable Collect Files'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_collect_files'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class EnableFileManager(AbstractSetting):
    def __init__(self):
        super(EnableFileManager, self).__init__()

        # Enable
        self.enable_toggle = QCheckBox(self.name())
        self.layout().addWidget(self.enable_toggle)

    def name(self):
        return 'Enable File Manager'

    def description(self):
        return ''

    def id(self):
        return 'hammer.enable_file_manager'

    def value(self):
        return self.enable_toggle.isChecked()

    def setValue(self, value):
        self.enable_toggle.setChecked(value)


class Section(QWidget):
    def __init__(self, name, description=''):
        super(Section, self).__init__()

        # Data
        self.__name = name
        self.__description = description
        self.__settings = []

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def description(self):
        return self.__description

    def setDescription(self, text):
        self.__description == text

    def addSetting(self, setting):
        self.__settings.append(setting)
        self.layout().addWidget(setting)

    def __contains__(self, item):
        for setting in self.__settings:
            if item in setting:
                return True
        return False


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

        # Data
        self.__section = section

    def setSection(self, section):
        self.__section = section

        # Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        self.setLayout(main_layout)

        main_layout.addWidget(self.__section)

        # Spacer
        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

    def setFilterPattern(self, pattern):
        raise NotImplementedError  # todo: filtering


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
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Filter
        self.filter_field = FilterField()
        left_layout.addWidget(self.filter_field)

        # Section View
        self.section_view = SectionView()
        self.filter_field.textChanged.connect(self.section_view.setFilterPattern)
        splitter.addWidget(self.section_view)

        # Section List
        general_section = Section('General')
        general_section.addSetting(EnableOpenFolder())
        general_section.addSetting(EnablePreviousFiles())
        general_section.addSetting(EnableSetInterpolation())
        general_section.addSetting(EnableSetSceneAudio())
        general_section.addSetting(EnablePlaySound())
        general_section.addSetting(EnableQuickSelection())
        general_section.addSetting(EnableCollectFiles())
        general_section.addSetting(EnableFileManager())

        temp_section = Section('Temp')

        sections = [general_section, temp_section]

        self.section_list_model = SectionListModel(self)
        self.section_list_model.setSectionList(sections)

        self.fuzzy_proxy_model = FuzzyFilterProxyModel(self)
        self.fuzzy_proxy_model.setSourceModel(self.section_list_model)
        self.fuzzy_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_field.textChanged.connect(self.fuzzy_proxy_model.setFilterPattern)

        self.section_list_view = SectionListView()
        self.section_list_view.setModel(self.fuzzy_proxy_model)
        self.section_list_view.clicked.connect(self.setCurrentSection)
        left_layout.addWidget(self.section_list_view)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply, Qt.Horizontal)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.rejected)
        self.buttons.clicked.connect(self.apply)
        main_layout.addWidget(self.buttons)

    def setCurrentSection(self, index):
        self.section_view.setSection(index.data(Qt.UserRole))

    def accept(self):
        pass

    def apply(self, button):
        if QDialogButtonBox.buttonRole(self.buttons, button) == QDialogButtonBox.ApplyRole:
            pass

    def reject(self):
        pass
