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

DEFAULT_SETTINGS = {
    'hammer.previous_files.first_start': True,
    'hammer.previous_files.enable': True,
    'hammer.previous_files.startup': True,
    'hammer.previous_files.check_file_existence': True,
    'hammer.previous_files.db_location': '$HOUDINI_USER_PREF_DIR',
    'hammer.previous_files.silent.manual_update': True,
    'hammer.previous_files.silent.disable_sims': False,

    'hammer.open_location.enable': True,
    'hammer.open_location.use_custom_explorer': False,
    'hammer.open_location.custom_explorer_path': '',

    'hammer.audio.play.enable': True,
    'hammer.audio.play.use_external_player': True,
    'hammer.audio.set_scene_audio.enable': True,

    'hammer.set_interpolation.enable': True,

    'hammer.select_parm_value.select.enable': True,
    'hammer.select_parm_value.select_font.enable': True,

    'hammer.shelf.copy_tool.enable': True,
    'hammer.shelf.edit_shelf_tools.enable': True
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
