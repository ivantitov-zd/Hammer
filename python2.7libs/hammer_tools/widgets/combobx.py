try:
    from PyQt5.QtWidgets import QComboBox
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QComboBox
    from PySide2.QtCore import Qt


class ComboBox(QComboBox):
    def findData(self, any_obj, role=Qt.UserRole, *args, **kwargs):
        if args or kwargs:
            return super(ComboBox, self).findData(any_obj, role, *args, **kwargs)

        for index in range(self.count()):
            obj = self.itemData(index, role)
            if obj == any_obj:
                return index
        return -1
