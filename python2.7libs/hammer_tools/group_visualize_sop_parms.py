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

from .quick_selection import FilterField, FuzzyListProxyModel
from .soputils import edgeGroupNames, Primitive, Point, Edge, Vertex, groupTypeFromParm


class GroupItem:
    def __init__(self, group, group_type, group_size):
        self.group = group
        self.group_type = group_type
        self.label = '{}   ({})'.format(group.name(), group_size)


class GroupListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(GroupListModel, self).__init__(parent)

        # Icons
        self.__polygon_icon = hou.qt.Icon('TOOLS_select_faces', 20, 20)
        self.__point_icon = hou.qt.Icon('TOOLS_select_points', 20, 20)
        self.__edge_icon = hou.qt.Icon('TOOLS_select_edges', 20, 20)
        self.__vertex_icon = hou.qt.Icon('TOOLS_select_vertices', 20, 20)

        self.__icons = {Primitive: self.__polygon_icon,
                        Point: self.__point_icon,
                        Edge: self.__edge_icon,
                        Vertex: self.__vertex_icon}

        # Data
        self.__data = ()

    def updateDataFromNode(self, node):
        self.beginResetModel()
        inputs = node.inputs()
        if inputs and inputs[0]:
            group_items = []
            geo = inputs[0].geometry()
            if geo is None:
                return
            group_items.extend(GroupItem(group, Primitive, len(group.iterPrims())) for group in geo.primGroups())
            group_items.extend(GroupItem(group, Point, len(group.iterPoints())) for group in geo.pointGroups())
            group_items.extend(GroupItem(group, Vertex, len(group.iterVertices())) for group in geo.vertexGroups())
            for edge_group_name in edgeGroupNames(geo):
                edge_group = geo.findEdgeGroup(edge_group_name)
                group_items.append(GroupItem(edge_group, Edge, len(edge_group.iterEdges())))
            self.__data = tuple(group_items)
        else:
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label
        elif role == Qt.UserRole:
            return item
        elif role == Qt.DecorationRole:
            return self.__icons[item.group_type]


class GroupListView(QListView):
    def __init__(self):
        super(GroupListView, self).__init__()

        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def selectGroup(self, group, group_type, group_size):
        model = self.model()
        indices = model.match(model.index(0, 0), Qt.DisplayRole, GroupItem(group, group_type, group_size).label)
        if indices:
            self.setCurrentIndex(indices[0])


class GroupListParms(QWidget):
    def __init__(self):
        super(GroupListParms, self).__init__()

        # Data
        self.__node = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Filter
        self.filter_field = FilterField()
        layout.addWidget(self.filter_field)

        # List
        self.list_model = GroupListModel(self)

        self.proxy_model = FuzzyListProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        self.filter_field.textChanged.connect(self.proxy_model.setFilterPattern)

        self.list_view = GroupListView()
        self.list_view.setModel(self.proxy_model)
        selection = self.list_view.selectionModel()
        selection.currentRowChanged.connect(self._setCurrentGroup)
        layout.addWidget(self.list_view)

    def updateGroupList(self, node=None, **kwargs):
        if node is not None:
            self.__node = node
        if self.__node is None:
            return
        self.list_model.updateDataFromNode(self.__node)
        group_name = self.__node.parm('group').evalAsString()
        group_type = groupTypeFromParm(self.__node.parm('grouptype'))
        geo = self.__node.geometry()
        try:
            if group_type == Primitive:
                group = geo.findPrimGroup(group_name)
                group_size = len(group.iterPrims())
            elif group_type == Point:
                group = geo.findPointGroup(group_name)
                group_size = len(group.iterPoints())
            elif group_type == Edge:
                group = geo.findEdgeGroup(group_name)
                group_size = len(group.iterEdges())
            elif group_type == Vertex:
                group = geo.findVertexGroup(group_name)
                group_size = len(group.iterVertices())
            else:  # group_type == Auto
                return
            self.list_view.selectGroup(group, group_type, group_size)
        except AttributeError:
            pass

    def _registerNodeCallbacks(self):
        self.__node.addEventCallback((hou.nodeEventType.InputRewired,
                                      hou.nodeEventType.InputDataChanged), self.updateGroupList)

    def _unregisterNodeCallbacks(self):
        self.__node.removeEventCallback((hou.nodeEventType.InputRewired,
                                         hou.nodeEventType.InputDataChanged), self.updateGroupList)

    def activate(self):
        self._registerNodeCallbacks()
        self.updateGroupList()

    def deactivate(self):
        self._unregisterNodeCallbacks()

    def setSourceNode(self, node):
        self.__node = node
        self.list_model.updateDataFromNode(node)

    def _setCurrentGroup(self):
        item = self.list_view.currentIndex().data(Qt.UserRole)
        try:
            with hou.undos.group('Parameter Change'):
                self.__node.parm('group').set(item.group.name())
                self.__node.parm('grouptype').set((-1, Primitive, Point, Edge, Vertex).index(item.group_type))
        except hou.ObjectWasDeleted:
            self.list_model.updateDataFromNode(node)
