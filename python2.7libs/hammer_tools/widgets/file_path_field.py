try:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog
except ImportError:
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog

import hou

from .input_field import InputField


class FilePathField(QWidget):
    def __init__(self, initial_path='', formats='All (*.*)'):
        super(FilePathField, self).__init__()

        self._formats = formats

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._text_field = InputField(initial_path)
        layout.addWidget(self._text_field)

        self._pick_location_button = QPushButton()
        self._pick_location_button.setToolTip('Pick location')
        self._pick_location_button.setFixedSize(24, 24)
        self._pick_location_button.setIcon(hou.qt.Icon('BUTTONS_chooser_folder', 16, 16))
        self._pick_location_button.clicked.connect(self.pickLocation)
        layout.addWidget(self._pick_location_button)

    def text(self):
        return self._text_field.text()

    def setText(self, text):
        self._text_field.setText(text)

    def path(self):
        return hou.expandString(self._text_field.text())

    def setPath(self, path):
        if path is None:
            self._text_field.setText('')

        if not path:
            return

        path = hou.text.collapseCommonVars(path, ['$HOUDINI_USER_PREF_DIR', '$HIP', '$JOB'])
        self._text_field.setText(path)

    def pickLocation(self):
        path = QFileDialog.getOpenFileName(self, 'Pick File', self.path(), self._formats)
        if path:
            self.setPath(path)
