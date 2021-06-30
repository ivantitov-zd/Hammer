try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from ..widgets import FilePathField


class PreviewSceneOptionsWidget(QWidget):
    def __init__(self):
        super(PreviewSceneOptionsWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._use_custom_geometry_toggle = QCheckBox('Use custom geometry')
        layout.addWidget(self._use_custom_geometry_toggle, 0, 0)

        self._custom_geometry_path_field = FilePathField('$JOB')
        self._custom_geometry_path_field.setDisabled(True)
        self._use_custom_geometry_toggle.toggled.connect(self._custom_geometry_path_field.setEnabled)
        layout.addWidget(self._custom_geometry_path_field, 0, 1)

        self._use_custom_hdri_toggle = QCheckBox('Use custom HDRI')
        layout.addWidget(self._use_custom_hdri_toggle, 1, 0)

        self._custom_hdri_path_field = FilePathField('$JOB', 'HDRI (*.hdr *.exr *.rat);; All (*.*)')
        self._custom_hdri_path_field.setDisabled(True)
        self._use_custom_hdri_toggle.toggled.connect(self._custom_hdri_path_field.setEnabled)
        layout.addWidget(self._custom_hdri_path_field, 1, 1)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addItem(spacer, 2, 0)

    def options(self):
        return {
            'use_custom_geo': self._use_custom_geometry_toggle.isChecked(),
            'custom_geo_path': self._custom_geometry_path_field.path() or None,
            'use_custom_hdri': self._use_custom_hdri_toggle.isChecked(),
            'custom_hdri_path': self._custom_hdri_path_field.path() or None
        }

    def setOptions(self, data):
        self._use_custom_geometry_toggle.setChecked(data.get('use_custom_geo', False))
        self._custom_geometry_path_field.setPath(data.get('custom_geo_path', ''))
        self._use_custom_hdri_toggle.setChecked(data.get('use_custom_hdri', False))
        self._custom_hdri_path_field.setPath(data.get('custom_hdri_path', ''))
