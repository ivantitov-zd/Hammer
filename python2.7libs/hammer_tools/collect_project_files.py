from __future__ import print_function

from hammer_tools.quick_selection import FilterField

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

GeometryFormats = ('.geo', '.bgeo', '.hclassic', '.bhclassic', '.geo.gz', '.geogz', '.bgeo.gz', '.bgeogz', '.hclassic.gz', '.hclassicgz',
                   '.bhclassic.gz', '.bhclassicgz', '.geo.sc', '.geosc', '.bgeo.sc', '.bgeosc', '.hclassic.sc', '.hclassicsc', '.bhclassic.sc',
                   '.bhclassicsc', '.json', '.bjson', '.json.gz', '.jsongz', '.bjson.gz', '.bjsongz', '.json.sc', '.jsonsc', '.bjson.sc',
                   '.bjsonsc', '.poly', '.bpoly', '.d', '.rib', '.flt', '.hgt', '.img', '.vdb', '.GoZ', '.bhclassic.lzma', '.bgeo.lzma',
                   '.hclassic.bz2', '.bgeo.bz2', '.pc', '.pmap', '.geo.lzma', '.off', '.iges', '.igs', '.ply', '.obj', '.pdb', '.hclassic.lzma',
                   '.lw', '.lwo', '.geo.bz2', '.bstl', '.eps', '.ai', '.stl', '.dxf', '.bhclassic.bz2', '.abc', '.fbx', '.usd', '.usda')
ImageFormats = ('.pic', '.pic.z', '.picz', '.pic.gz', '.picgz', '.tbf', '.dsm', '.picnc', '.piclc', '.rgb', '.rgba', '.sgi', '.tif', '.tif3',
                '.tif16', '.tif32', '.tiff', '.yuv', '.pix', '.als', '.cin', '.kdk', '.jpg', '.jpeg', '.png', '.psd', '.psb', '.si', '.tga',
                '.vst', '.vtg', '.rla', '.rla16', '.rlb', '.rlb16', '.bmp', '.hdr', '.ies', '.qtl')
TextureFormats = ('.exr', '.rat', '.tex', '.ptx', '.ptex')
AudioFormats = ('.aif', '.aifc', '.aiff', '.fbx', '.flac', '.it', '.mod', '.mp2', '.mp3', '.ogg', '.s3m', '.spx', '.wav', '.xm')
AnimationFormats = ('.bchan', '.bchn', '.bclip', '.bclip.sc', '.bcliplc', '.bclipnc', '.chan', '.chn', '.clip')
AnyDataFormats = ('.csv', '.txt', '.db')

EDITABLE_ICON = hou.qt.Icon('TOP_status_cooked', 20, 20)
NOT_EDITABLE_ICON = hou.qt.Icon('TOP_status_error', 20, 20)


def isParmEditable(parm):
    return parm.node().parent().isEditable() and not parm.isLocked()


class Link:
    def __init__(self, parm):
        self.parm = parm
        self.enabled = True

    def setEnabled(self, enable=True):
        self.enabled = enable

    def _solveFileLinks(self):
        raise NotImplementedError

    def relink(self, new_location):
        raise NotImplementedError


class LinkModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(LinkModel, self).__init__(parent)

        self.nodes = {}
        self.parms = {}
        self.updateDataFromScene()

    def updateDataFromScene(self):
        self.beginResetModel()
        self.nodes = {}
        self.parms = {}
        for parm, raw_path in hou.fileReferences():
            if parm is None:
                continue
            node = parm.node()
            self.parms[parm] = node
            if node not in self.nodes:
                self.nodes[node] = {'enable': True, 'parms': [parm]}
            else:
                self.nodes[node]['parms'].append(parm)
        self.endResetModel()

    def headerData(self, section, orientation, role):
        names = ('Name', '', '')
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return names[section]

    def columnCount(self, parent):
        return 3

    def rowCount(self, parent):
        if not parent.isValid():  # Node
            return len(self.nodes)
        elif not parent.parent().isValid():  # Parm
            return len(self.nodes[parent.internalPointer()]['parms'])
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():  # Root
            return
        o = index.internalPointer()
        column = index.column()
        if index.parent().isValid():  # Parm
            if role == Qt.DisplayRole:
                if column == 0:
                    return o.name()
                elif column == 1:
                    return 'Enabled'
            elif role == Qt.DecorationRole:
                if column == 0:
                    if isParmEditable(o):
                        return EDITABLE_ICON
                    else:
                        return NOT_EDITABLE_ICON
        else:  # Node
            if role == Qt.DisplayRole:
                if column == 0:
                    return o.name()
                elif column == 1:
                    return o.path()
            elif role == Qt.ToolTipRole:
                if column == 1:
                    return o.path()
            elif role == Qt.DecorationRole:
                if column == 0:
                    if o.parent().isEditable():
                        return EDITABLE_ICON
                    else:
                        return NOT_EDITABLE_ICON

    def parent(self, index):
        if not index.isValid():  # Root
            return QModelIndex()

        o = index.internalPointer()
        if isinstance(o, hou.Node):  # Node
            return QModelIndex()

        # Parm
        node = self.parms[o]
        row = self.nodes.keys().index(node)
        return self.createIndex(row, 0, node)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():  # Node
            return self.createIndex(row, column, self.nodes.keys()[row])
        else:  # Parm
            return self.createIndex(row, column, self.nodes[parent.internalPointer()]['parms'][row])


class CollectProjectFiles(QDialog):
    def __init__(self, parent=None):
        super(CollectProjectFiles, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Collect Project Files')
        self.setStyleSheet(hou.qt.styleSheet())
        self.resize(800, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Location
        location_layout = QHBoxLayout()
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.setSpacing(4)
        main_layout.addLayout(location_layout)

        location_label = QLabel('Location')
        location_layout.setAlignment(Qt.AlignVCenter)
        location_layout.addWidget(location_label)

        self.location_field = QLineEdit('$HIP/collected/')
        location_layout.addWidget(self.location_field)

        choose_location_button = hou.qt.FileChooserButton()
        choose_location_button.setFileChooserTitle('Folder')
        choose_location_button.setFileChooserFilter(hou.fileType.Directory)
        choose_location_button.setFileChooserMode(hou.fileChooserMode.Read)
        choose_location_button.fileSelected.connect(self.setFolder)
        location_layout.addWidget(choose_location_button)

        # Options
        links_group = QGroupBox('Links')
        links_group_layout = QVBoxLayout(links_group)
        links_group_layout.setContentsMargins(4, 4, 4, 4)
        links_group_layout.setSpacing(4)

        absolute_radio = QRadioButton('Absolute')
        links_group_layout.addWidget(absolute_radio)

        relative_radio = QRadioButton('Relative')
        relative_radio.setChecked(True)
        links_group_layout.addWidget(relative_radio)

        # Variable
        variable_group = QGroupBox('Variable')
        variable_group_layout = QVBoxLayout(variable_group)
        variable_group_layout.setContentsMargins(4, 4, 4, 4)
        variable_group_layout.setSpacing(4)
        links_group_layout.addWidget(variable_group)

        hip_radio = QRadioButton('$HIP')
        hip_radio.setChecked(True)
        relative_radio.toggled.connect(hip_radio.setEnabled)
        variable_group_layout.addWidget(hip_radio)

        job_radio = QRadioButton('$JOB')
        relative_radio.toggled.connect(job_radio.setEnabled)
        variable_group_layout.addWidget(job_radio)

        custom_radio = QRadioButton('Custom')
        relative_radio.toggled.connect(custom_radio.setEnabled)
        variable_group_layout.addWidget(custom_radio)

        output_log_toggle = QCheckBox('Output log')
        output_log_toggle.setChecked(True)

        open_location_when_finished_toggle = QCheckBox('Open location when finished')
        open_location_when_finished_toggle.setChecked(True)

        # Structure
        self.filter_field = FilterField()

        self.node_tree = QTreeView()
        self.link_model = LinkModel(self)
        self.node_tree.setModel(self.link_model)
        self.node_tree.expandAll()

        # Tabs
        tabs = QTabWidget()

        options_widget = QWidget()
        options_widget_layout = QVBoxLayout(options_widget)
        options_widget_layout.setContentsMargins(4, 4, 4, 4)
        options_widget_layout.setSpacing(4)

        options_widget_layout.addWidget(links_group)
        options_widget_layout.addWidget(output_log_toggle)
        options_widget_layout.addWidget(open_location_when_finished_toggle)
        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        options_widget_layout.addSpacerItem(spacer)

        tabs.addTab(options_widget, 'Options')

        tree_widget = QWidget()
        tree_widget_layout = QVBoxLayout(tree_widget)
        tree_widget_layout.setContentsMargins(0, 0, 0, 0)
        tree_widget_layout.setSpacing(4)
        tree_widget_layout.addWidget(self.filter_field)
        tree_widget_layout.addWidget(self.node_tree)
        tabs.addTab(tree_widget, 'Tree')

        main_layout.addWidget(tabs)

        # Execution
        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run)
        main_layout.addWidget(self.run_button)

        self.progress_line = QProgressBar()
        self.progress_line.setFixedHeight(4)
        self.progress_line.setStyleSheet('border: 0px;')
        main_layout.addWidget(self.progress_line)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def updateTree(self):
        self.filter_field.clear()
        self.link_model.updateDataFromScene()
        raise NotImplementedError

    def setFolder(self, path):
        self.location_field.setText(path)
        self.updateTree()

    def run(self):
        self.filter_field.clear()
        raise NotImplementedError


def collectProjectFiles():
    hou.session.hammer_collect_project_files = CollectProjectFiles(hou.qt.mainWindow())
    hou.session.hammer_collect_project_files.show()
