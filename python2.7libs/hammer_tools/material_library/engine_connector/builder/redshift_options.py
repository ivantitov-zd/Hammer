try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox
except ImportError:
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QCheckBox


class RedshiftBuildOptions(QWidget):
    def __init__(self):
        super(RedshiftBuildOptions, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._use_tri_planar_toggle = QCheckBox('Use Tri-Planar')
        layout.addWidget(self._use_tri_planar_toggle)

    def options(self):
        return {
            'use_tri_planar': self._use_tri_planar_toggle.isChecked()
        }

    def setOptions(self, options):
        use_tri_planar = options.get('use_tri_planar')
        if use_tri_planar is not None:
            self._use_tri_planar_toggle.setChecked(use_tri_planar)
