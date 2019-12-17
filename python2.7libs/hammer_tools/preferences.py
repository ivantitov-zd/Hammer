from __future__ import print_function

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

PREF_FILE = hou.homeHoudiniDirectory() + '/hammer_tools.pref'


class AbstractSetting(QWidget):
    # Signals
    changed = Signal(int)

    def __init__(self):
        super(AbstractSetting, self).__init__()

    def id(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError


class SettingGroup(QGroupBox):
    def __init__(self, name):
        self.setTitle(name)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

    def addSetting(self, setting):
        self.layout().addWidget(setting)


class OpenFolderSetting(AbstractSetting):
    def __init__(self):
        super(OpenFolderSetting, self).__init__()

    def id(self):
        pass

    def name(self):
        return 'Open Folder'

    def description(self):
        return None


class Section(QWidget):
    def __init__(self, name, description=''):
        super(Section, self).__init__()

        self.name = name
        self.description = description

        self.__settings = []

    def addSetting(self, setting):
        self.__settings.append(setting)

    def __contains__(self, item):
        for setting in self.__settings:
            if item in setting:
                return True
        return False


class SectionListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(SectionListModel, self).__init__(parent)

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
            return self.__sections[index.row()].name
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

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

    def clear(self):
        self.__section = None

    def setSection(self, section):
        self.clear()
        self.__section = section


class HammerPreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super(HammerPreferencesDialog, self).__init__(parent, Qt.Window)

        # UI
        self.setWindowTitle('Hammer Tools: Preferences')
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        main_layout.addLayout(left_layout)

        # Filter
        self.filter_field = FilterField()
        left_layout.addWidget(self.filter_field)

        # Section
        self.section_view = SectionView()
        main_layout.addWidget(self.section_view)

        # Section List
        general_section = Section('General')
        general_section.addSetting(OpenFolderSetting())

        sections = [general_section]

        self.section_list_model = SectionListModel(self)
        self.section_list_model.setSectionList(sections)

        self.section_list_view = SectionListView()
        self.section_list_view.setModel(self.section_list_model)
        self.section_list_view.clicked.connect(self.setCurrentSection)
        left_layout.addWidget(self.section_list_view)

    def setCurrentSection(self, index):
        self.section_view.setSection(index.data(Qt.UserRole))
