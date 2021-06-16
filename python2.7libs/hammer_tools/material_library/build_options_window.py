try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou

from ..widgets import ComboBox
from .engine_connector import EngineConnector


class BuildOptionsWindow(QDialog):
    def __init__(self, builder=None, parent=None):
        super(BuildOptionsWindow, self).__init__(parent)

        self._widget = None

        self.setWindowTitle('Hammer: Material build options')
        self.setWindowIcon(hou.qt.Icon('SHELF_preflight', 32, 32))
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._target_engine_combo = ComboBox()
        self._target_engine_combo.setMinimumWidth(100)
        self._target_engine_combo.setToolTip('Target rendering engine')
        for engine in EngineConnector.engines(lambda e: e.isAvailable() and e.builders()):
            self._target_engine_combo.addItem(engine.icon(), engine.name(), engine)
        if builder:
            index = self._target_engine_combo.findData(builder.engine)
        else:
            index = self._target_engine_combo.findData(EngineConnector.currentEngine())
        self._target_engine_combo.setCurrentIndex(index if index > -1 else 0)
        self._target_engine_combo.currentIndexChanged.connect(self.onCurrentEngineChanged)
        layout.addWidget(self._target_engine_combo)

        self._target_builder_combo = ComboBox()
        self._target_builder_combo.setMinimumWidth(140)
        self._target_builder_combo.setToolTip('Target builder')
        self.updateEngineBuilderList()
        if builder:
            index = self._target_builder_combo.findData(builder)
        else:
            index = 0
        self._target_builder_combo.setCurrentIndex(index)
        self._target_builder_combo.currentIndexChanged.connect(self.replaceOptionsWidget)
        layout.addWidget(self._target_builder_combo)
        self.replaceOptionsWidget()

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        layout.addLayout(button_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        button_layout.addSpacerItem(spacer)

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_button)

        self._ok_button = QPushButton('OK')
        self._ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self._ok_button)

    def options(self):
        data = {'builder': self._target_builder_combo.currentData()}
        if self._widget is not None:
            data.update(self._widget.options())
        return data

    def setOptions(self, options):
        if self._widget is None:
            return

        self._widget.setOptions(options)

    def replaceOptionsWidget(self):
        if self._widget is not None:
            self.layout().takeAt(2).widget().deleteLater()
        builder = self._target_builder_combo.currentData()
        self._widget = builder.buildOptionsWidget()
        if self._widget is not None:
            self.layout().insertWidget(2, self._widget)

    def updateEngineBuilderList(self):
        self._target_builder_combo.blockSignals(True)
        self._target_builder_combo.clear()
        engine = self._target_engine_combo.currentData()
        for builder in engine.builders():
            self._target_builder_combo.addItem(builder.name(), builder)
        self._target_builder_combo.blockSignals(False)

    def onCurrentEngineChanged(self, index):
        self.updateEngineBuilderList()
        self.replaceOptionsWidget()

    def hideEvent(self, event):
        self.deleteLater()
