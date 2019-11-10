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

hou.homeHoudiniDirectory()


class PreviousFiles(QDialog):
    def __init__(self, parent=None):
        super(PreviousFiles, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Welcome')
        self.resize(700, 500)
        self.setStyleSheet(hou.qt.styleSheet())

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.mainLayout.setSpacing(4)

        self.leftVerticalLayout = QVBoxLayout()
        self.leftVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftVerticalLayout.setSpacing(0)
        self.mainLayout.addLayout(self.leftVerticalLayout)

        self.new = QPushButton('New File')
        self.new.setMinimumWidth(100)
        self.new.clicked.connect(self.createNewHip)
        self.leftVerticalLayout.addWidget(self.new)

        self.openMenu = QMenu(self)
        openInManualMode = QAction('Open in Manual Mode', self)
        self.openMenu.addAction(openInManualMode)

        self.open = QToolButton()
        self.open.setMenu(self.openMenu)
        self.open.setStyleSheet('border-radius: 1; border-style: none')
        self.open.setMinimumWidth(100)
        self.open.setText('Open...')
        self.open.clicked.connect(self.openHip)
        self.leftVerticalLayout.addWidget(self.open)

        self.merge = QPushButton('Merge...')
        self.merge.clicked.connect(self.mergeHips)
        self.leftVerticalLayout.addWidget(self.merge)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.leftVerticalLayout.addSpacerItem(spacer)

        self.rightVerticalLayout = QVBoxLayout()
        self.rightVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.rightVerticalLayout.setSpacing(0)
        self.mainLayout.addLayout(self.rightVerticalLayout)

        self.filter_field = FilterField()
        self.rightVerticalLayout.addWidget(self.filter_field)

        self.list_view = QTreeView()
        self.rightVerticalLayout.addWidget(self.list_view)

    def createNewHip(self):
        hou.hipFile.clear()
        self.hide()

    def openHip(self):
        files = hou.ui.selectFile(title='Open', file_type=hou.fileType.Hip, chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            hou.hipFile.load(files[0])
            self.hide()

    def mergeHips(self):
        files = hou.ui.selectFile(title='Merge', file_type=hou.fileType.Hip, multiple_select=True, chooser_mode=hou.fileChooserMode.Read).split(' ; ')
        if files and files[0]:
            for file in tuple(map(lambda f: hou.expandString(f), files)):
                hou.hipFile.merge(file)
            self.hide()


def show(modal=False):
    if not hasattr(hou.session, 'hammer_previous_files'):
        hou.session.hammer_previous_files = PreviousFiles(hou.qt.mainWindow())
    if modal:
        hou.session.hammer_previous_files.exec_()
    else:
        hou.session.hammer_previous_files.setParent(hou.qt.mainWindow())
        hou.session.hammer_previous_files.show()
