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


def mergeObjects(nodes, name=None, stash=False, add_groups=False, add_name_attrib=False, attrib_name='name', delete_original=False):
    if not nodes:
        return
    with hou.undos.group('Merge Objects'):
        geo = nodes[0].parent().createNode('geo', name)
        merge = geo.createNode('merge', name)
        merge.setDisplayFlag(True)
        for node in nodes:
            new_node = geo.createNode('object_merge')
            object_merge = new_node
            new_node.parm('objpath1').set(node.path())
            if add_groups:
                new_node = new_node.createOutputNode('groupcreate')
                new_node.parm('groupname').set(node.name())
            if add_name_attrib:
                new_node = new_node.createOutputNode('name')
                new_node.parm('attribname').set(attrib_name or 'name')
                new_node.parm('name1').set(node.name())
            if stash:
                new_node = new_node.createOutputNode('stash')
                new_node.setName(node.name(), True)
                new_node.parm('stashinput').pressButton()
                input_nodes = new_node.inputs()
                while input_nodes:
                    input_node = input_nodes[0]
                    input_nodes = input_node.inputs()
                    input_node.destroy()
                if delete_original:
                    node.destroy()
            else:
                object_merge.setName(node.name(), True)
            merge.setNextInput(new_node)
        geo.layoutChildren()


class MergeObjectsOptions(QDialog):
    def __init__(self, parent=None):
        super(MergeObjectsOptions, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Merge Options')
        self.setStyleSheet(hou.qt.styleSheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText('New name')
        main_layout.addWidget(self.name_field)

        self.stash_toggle = QCheckBox('Stash Geometry')
        main_layout.addWidget(self.stash_toggle)

        self.delete_original_toggle = QCheckBox('Delete Sources')
        self.delete_original_toggle.setChecked(True)
        self.delete_original_toggle.setEnabled(False)
        self.stash_toggle.stateChanged.connect(self.delete_original_toggle.setEnabled)
        main_layout.addWidget(self.delete_original_toggle)

        self.group_toggle = QCheckBox('Add Groups')
        main_layout.addWidget(self.group_toggle)

        self.name_attrib_toggle = QCheckBox('Add Name Attribute')
        main_layout.addWidget(self.name_attrib_toggle)

        self.name_attrib_name_field = QLineEdit('name')
        self.name_attrib_name_field.setPlaceholderText('Attribute name')
        self.name_attrib_name_field.setEnabled(False)
        self.name_attrib_toggle.stateChanged.connect(self.name_attrib_name_field.setEnabled)
        main_layout.addWidget(self.name_attrib_name_field)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    @classmethod
    def getOptions(cls):
        dialog = cls(hou.qt.mainWindow())
        enable = dialog.exec_()
        return {'enable': enable,
                'name': dialog.name_field.text().strip() if dialog.name_field.text().strip() else None,
                'stash': dialog.stash_toggle.isChecked(),
                'delete_original': dialog.delete_original_toggle.isChecked(),
                'add_groups': dialog.group_toggle.isChecked(),
                'add_name_attrib': dialog.name_attrib_toggle.isChecked(),
                'attrib_name': dialog.name_attrib_name_field.text()} if enable else {'enable': enable}


def mergeSelectedObjects():
    selected_nodes = hou.selectedNodes()
    if selected_nodes and selected_nodes[0].type().category() == hou.objNodeTypeCategory():
        options = MergeObjectsOptions.getOptions()
        if options.pop('enable'):
            mergeObjects(selected_nodes, **options)
