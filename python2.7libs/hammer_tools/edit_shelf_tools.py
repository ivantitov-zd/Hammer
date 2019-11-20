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

from .quick_selection import FilterField, FuzzyFilterProxyModel


class ShelfToolsModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ShelfToolsModel, self).__init__(parent)

        self.__tool_list = ()
        # self.__contained_tool_list = ()

    def updateDataFromShelf(self, shelf):
        self.beginResetModel()
        self.__tool_list = shelf.tools()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__tool_list)

    def data(self, index, role):
        tool = self.__tool_list[index.row()]
        if role == Qt.DisplayRole:
            return '{} ({})'.format(tool.label(), tool.name())
        elif role == Qt.UserRole:
            return tool


class EditShelfTools(QDialog):
    def __init__(self, parent=None):
        super(EditShelfTools, self).__init__(parent, Qt.Window)

        self.resize(600, 400)
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Tool list
        self.tool_list_model = ShelfToolsModel(self)
        self.tool_list_filter_model = FuzzyFilterProxyModel(self)
        self.tool_list_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.tool_list_filter_model.setSourceModel(self.tool_list_model)
        self.tool_list_view = QListView()
        self.tool_list_view.setModel(self.tool_list_filter_model)

        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(self.tool_list_filter_model.setFilterPattern)

        main_layout.addWidget(self.filter_field)
        main_layout.addWidget(self.tool_list_view)

    def show(self, shelf):
        self.setWindowTitle('Edit Shelf Tools: {} ({})'.format(shelf.label(), shelf.name()))
        self.filter_field.setFocus()
        self.filter_field.selectAll()
        self.tool_list_model.updateDataFromShelf(shelf)
        super(EditShelfTools, self).show()


def editShelf(shelf_name):
    shelf = hou.shelves.shelves().get(shelf_name)
    if shelf:
        if not hasattr(hou.session, 'hammer_edit_shelf'):
            hou.session.hammer_edit_shelf = EditShelfTools(hou.qt.mainWindow())
        hou.session.hammer_edit_shelf.show(shelf)
