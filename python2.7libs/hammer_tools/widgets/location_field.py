try:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog
except ImportError:
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog

import hou

from .input_field import InputField


class LocationField(QWidget):
    def __init__(self, initial_location=''):
        super(LocationField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.text_field = InputField(initial_location)
        self.layout().addWidget(self.text_field)

        self.pick_location_button = QPushButton()
        self.pick_location_button.setToolTip('Pick location')
        self.pick_location_button.setFixedSize(24, 24)
        self.pick_location_button.setIcon(hou.qt.Icon('BUTTONS_chooser_folder', 16, 16))
        self.pick_location_button.clicked.connect(self.pickLocation)
        self.layout().addWidget(self.pick_location_button)

    def text(self):
        return self.text_field.text()

    def setText(self, text):
        self.text_field.setText(text)

    def path(self):
        return hou.expandString(self.text_field.text())

    def setPath(self, path):
        if path is None:
            self.text_field.setText('')

        if not path:
            return

        path = hou.text.collapseCommonVars(path, ['$HOUDINI_USER_PREF_DIR', '$HIP', '$JOB'])
        self.text_field.setText(path)

    def pickLocation(self):
        path = QFileDialog.getExistingDirectory(self, 'Pick Location', self.path())
        self.setPath(path)
