try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QCheckBox
    from PySide2.QtCore import Qt

from ....widgets import ComboBox


class RedshiftBuildOptions(QWidget):
    def __init__(self):
        super(RedshiftBuildOptions, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._uv_mode = ComboBox()
        self._uv_mode.addItem('Normal UV', 'normal')
        self._uv_mode.addItem('UDIM', 'udim')
        self._uv_mode.addItem('UV Tile', 'uvtile')
        layout.addWidget(self._uv_mode)

        self._add_color_controls_toggle = QCheckBox('Add color controls')
        layout.addWidget(self._add_color_controls_toggle)

        self._add_range_controls_toggle = QCheckBox('Add range controls')
        layout.addWidget(self._add_range_controls_toggle)

        self._use_tri_planar_toggle = QCheckBox('Use Tri-Planar')
        layout.addWidget(self._use_tri_planar_toggle)

        self._use_sprite_toggle = QCheckBox('Use Sprite for Opacity')
        layout.addWidget(self._use_sprite_toggle)

    def options(self):
        return {
            'uv_mode': self._uv_mode.currentData(),
            'add_color_controls': self._add_color_controls_toggle.isChecked(),
            'add_range_controls': self._add_range_controls_toggle.isChecked(),
            'use_tri_planar': self._use_tri_planar_toggle.isChecked(),
            'use_sprite': self._use_sprite_toggle.isChecked()
        }

    def setOptions(self, options):
        uv_mode = options.get('uv_mode')
        if uv_mode is not None:
            self._uv_mode.setCurrentIndex(self._uv_mode.findData(uv_mode))

        add_color_controls = options.get('add_color_controls')
        if add_color_controls is not None:
            self._add_color_controls_toggle.setChecked(add_color_controls)

        add_range_controls = options.get('add_range_controls')
        if add_range_controls is not None:
            self._add_range_controls_toggle.setChecked(add_range_controls)

        use_tri_planar = options.get('use_tri_planar')
        if use_tri_planar is not None:
            self._use_tri_planar_toggle.setChecked(use_tri_planar)

        use_sprite = options.get('use_sprite')
        if use_sprite is not None:
            self._use_sprite_toggle.setChecked(use_sprite)
