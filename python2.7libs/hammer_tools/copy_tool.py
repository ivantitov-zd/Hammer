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


class ShelfListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ShelfListModel, self).__init__(parent)

        self.__shelf_list = {}

    def updateData(self):
        self.__shelf_list = hou.shelves.shelves()

    def rowCount(self, parent):
        return len(self.__shelf_list)

    def data(self, index, role):
        shelf = self.__shelf_list.values()[index.row()]
        if role == Qt.DisplayRole:
            return '{} ({})'.format(shelf.label(), shelf.name())
        elif role == Qt.UserRole:
            return shelf


class CopyShelfTool(QDialog):
    def __init__(self, parent=None):
        super(CopyShelfTool, self).__init__(parent, Qt.Window)

        self.resize(400, 400)
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Shelf list
        self.shelf_list_model = ShelfListModel(self)
        self.shelf_list_view = QListView()
        self.shelf_list_view.setModel(self.shelf_list_model)
        self.shelf_list_view.doubleClicked.connect(self.copyTool)

        main_layout.addWidget(self.shelf_list_view)

    def copyTool(self):
        pass

    def show(self, tool):
        self.setWindowTitle('Copy [{}] Tool to another Shelf'.format(tool.label()))
        self.shelf_list_model.updateData()
        super(CopyShelfTool, self).show()


def copyTool(tool_name):
    tool = hou.shelves.tool(tool_name)
    if tool:
        if not hasattr(hou.session, 'hammer_copy_shelf_tool'):
            hou.session.hammer_copy_shelf_tool = CopyShelfTool(hou.qt.mainWindow())
        hou.session.hammer_copy_shelf_tool.show(tool)
