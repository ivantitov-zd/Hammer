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


class EmprtTool:
    @staticmethod
    def name():
        return ''

    @staticmethod
    def label():
        return ''


class ShelfToolsModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ShelfToolsModel, self).__init__(parent)

        self.__tool_list = []
        self.shelf = None

    def updateDataFromShelf(self, shelf):
        self.beginResetModel()
        self.__tool_list = list(shelf.tools())
        self.shelf = shelf
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__tool_list)

    def data(self, index, role):
        tool = self.__tool_list[index.row()]
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return '{} ({})'.format(tool.label(), tool.name())
        elif role == Qt.UserRole:
            return tool

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self.__tool_list.insert(row + i, EmprtTool)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            self.__tool_list.pop(row + i)
        self.endRemoveRows()
        return True

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.DisplayRole:
            self.__tool_list[index.row()] = hou.shelves.tool(value)
            print(self.__tool_list[index.row()], index.row())
            return True
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def supportedDragActions(self):
        return Qt.MoveAction

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return 'houdini/shelf.tool',

    def canDropMimeData(self, data, action, row, column, parent):
        return action == Qt.MoveAction and data.hasFormat('houdini/shelf.tool')

    def mimeData(self, indexes):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                stream.writeString(self.data(index, Qt.UserRole).name())
        mime_data.setData('houdini/shelf.tool', encoded_data)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True
        elif action != Qt.MoveAction:
            return False

        encoded_data = data.data('houdini/shelf.tool')
        stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        new_items = []
        rows = 0

        while not stream.atEnd():
            new_items.append(stream.readString())
            rows += 1

        self.insertRows(row, rows, QModelIndex())
        for text in new_items:
            index = self.index(row, 0, QModelIndex())
            self.setData(index, text, Qt.DisplayRole)
            row += 1

        return True


class AllToolsModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(AllToolsModel, self).__init__(parent)

        self.__tool_list = []
        self.shelf = None

    def updateDataFromShelf(self, shelf):
        self.beginResetModel()
        shelf_tools = shelf.tools()
        tool_list = []
        for name, tool in hou.shelves.tools().items():
            if tool not in shelf_tools:
                tool_list.append(tool)
        self.__tool_list = tool_list
        self.shelf = shelf
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__tool_list)

    def data(self, index, role):
        tool = self.__tool_list[index.row()]
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return '{} ({})'.format(tool.label(), tool.name())
        elif role == Qt.UserRole:
            return tool

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self.__tool_list.insert(row + i, EmprtTool)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            self.__tool_list.pop(row + i)
        self.endRemoveRows()
        return True

    def setData(self, index, value, role):
        if role == Qt.DisplayRole:
            self.__tool_list[index.row()] = hou.shelves.tool(value)
            return True
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def supportedDragActions(self):
        return Qt.MoveAction

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return 'houdini/shelf.tool',

    def canDropMimeData(self, data, action, row, column, parent):
        return action == Qt.MoveAction and data.hasFormat('houdini/shelf.tool')

    def mimeData(self, indexes):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                stream.writeString(self.data(index, Qt.UserRole).name())
        mime_data.setData('houdini/shelf.tool', encoded_data)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True
        elif action != Qt.MoveAction:
            return False

        encoded_data = data.data('houdini/shelf.tool')
        stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        new_items = []
        rows = 0

        while not stream.atEnd():
            new_items.append(stream.readString())
            rows += 1

        self.insertRows(row, rows, QModelIndex())
        for text in new_items:
            index = self.index(row, 0, QModelIndex())
            self.setData(index, text, Qt.DisplayRole)
            row += 1

        return True


class EditShelfTools(QDialog):
    def __init__(self, parent=None):
        super(EditShelfTools, self).__init__(parent, Qt.Window)

        self.resize(600, 400)
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        splitter = QSplitter(Qt.Vertical)

        # Filter Field
        self.filter_field = FilterField()
        main_layout.addWidget(self.filter_field)

        # Shelf tools
        self.shelf_tool_list_model = ShelfToolsModel(self)
        self.shelf_tool_list_filter_model = FuzzyFilterProxyModel(self)
        self.shelf_tool_list_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.shelf_tool_list_filter_model.setSourceModel(self.shelf_tool_list_model)
        self.shelf_tool_list_view = QListView()
        self.shelf_tool_list_view.setAlternatingRowColors(True)
        self.shelf_tool_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.shelf_tool_list_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.shelf_tool_list_view.setDragEnabled(True)
        self.shelf_tool_list_view.setAcceptDrops(True)
        self.shelf_tool_list_view.setDropIndicatorShown(True)
        self.shelf_tool_list_view.setModel(self.shelf_tool_list_filter_model)
        splitter.addWidget(self.shelf_tool_list_view)

        # All tools
        self.all_tool_list_model = AllToolsModel(self)
        self.all_tool_list_filter_model = FuzzyFilterProxyModel(self)
        self.all_tool_list_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.all_tool_list_filter_model.setSourceModel(self.all_tool_list_model)
        self.all_tool_list_view = QListView()
        self.all_tool_list_view.setAlternatingRowColors(True)
        self.all_tool_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.all_tool_list_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.all_tool_list_view.setDragEnabled(True)
        self.all_tool_list_view.setAcceptDrops(True)
        self.all_tool_list_view.setDropIndicatorShown(True)
        self.all_tool_list_view.setModel(self.all_tool_list_filter_model)
        splitter.addWidget(self.all_tool_list_view)

        self.filter_field.textChanged.connect(self.filter)

        main_layout.addWidget(splitter)

    def filter(self, pattern):
        self.shelf_tool_list_filter_model.setFilterPattern(pattern)
        self.all_tool_list_filter_model.setFilterPattern(pattern)

    def show(self, shelf):
        self.setWindowTitle('Edit Shelf Tools: {} ({})'.format(shelf.label(), shelf.name()))
        self.filter_field.setFocus()
        self.filter_field.selectAll()
        self.shelf_tool_list_model.updateDataFromShelf(shelf)
        self.all_tool_list_model.updateDataFromShelf(shelf)
        super(EditShelfTools, self).show()


def editShelf(shelf_name):
    shelf = hou.shelves.shelves().get(shelf_name)
    if shelf:
        if not hasattr(hou.session, 'hammer_edit_shelf'):
            hou.session.hammer_edit_shelf = EditShelfTools(hou.qt.mainWindow())
        hou.session.hammer_edit_shelf.show(shelf)
