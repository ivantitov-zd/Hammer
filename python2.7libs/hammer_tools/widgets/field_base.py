try:
    from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QHBoxLayout, QWidget, QLabel
    from PySide2.QtCore import Qt


class FieldBase(QWidget):
    def __init__(self, label_text=None, label_width=None, label_alignment=Qt.AlignLeft | Qt.AlignVCenter):
        super(FieldBase, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label_text is not None:
            self.label = QLabel(label_text)

            if label_width is not None:
                self.label.setFixedWidth(label_width)

            self.label.setAlignment(label_alignment)
            layout.addWidget(self.label)
