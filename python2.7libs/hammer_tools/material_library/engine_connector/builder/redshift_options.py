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

        self.add_color_controls_toggle = QCheckBox('Add color controls')
        layout.addWidget(self.add_color_controls_toggle)

        self.add_range_controls_toggle = QCheckBox('Add range controls')
        layout.addWidget(self.add_range_controls_toggle)

        self.use_tri_planar_toggle = QCheckBox('Use Tri-Planar')
        layout.addWidget(self.use_tri_planar_toggle)

        self.uv_mode_combo = ComboBox()
        self.uv_mode_combo.addItem('Normal UV', 'normal')
        self.uv_mode_combo.addItem('UDIM', 'udim')
        self.uv_mode_combo.addItem('UV Tile', 'uvtile')
        self.use_tri_planar_toggle.toggled.connect(self.uv_mode_combo.setDisabled)
        layout.addWidget(self.uv_mode_combo)

        self.use_sprite_toggle = QCheckBox('Use Sprite for Opacity')
        layout.addWidget(self.use_sprite_toggle)

    def options(self):
        return {
            'uv_mode': self.uv_mode_combo.currentData() if not self.use_tri_planar_toggle.isChecked() else 'normal',
            'add_color_controls': self.add_color_controls_toggle.isChecked(),
            'add_range_controls': self.add_range_controls_toggle.isChecked(),
            'use_tri_planar': self.use_tri_planar_toggle.isChecked(),
            'use_sprite': self.use_sprite_toggle.isChecked()
        }

    def setOptions(self, options):
        uv_mode = options.get('uv_mode')
        if uv_mode is not None:
            self.uv_mode_combo.setCurrentIndex(self.uv_mode_combo.findData(uv_mode))

        add_color_controls = options.get('add_color_controls')
        if add_color_controls is not None:
            self.add_color_controls_toggle.setChecked(add_color_controls)

        add_range_controls = options.get('add_range_controls')
        if add_range_controls is not None:
            self.add_range_controls_toggle.setChecked(add_range_controls)

        use_tri_planar = options.get('use_tri_planar')
        if use_tri_planar is not None:
            self.use_tri_planar_toggle.setChecked(use_tri_planar)

        use_sprite = options.get('use_sprite')
        if use_sprite is not None:
            self.use_sprite_toggle.setChecked(use_sprite)
