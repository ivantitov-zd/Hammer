from datetime import timedelta
from time import time

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
import numpy as np

import hou

from . import ui
from .text import MONOSPACE_FONT


class TimeEstimation(object):
    Off = 0
    First = 1
    Last = 2
    Minimum = 3
    Maximum = 4
    Mean = 5
    Median = 6


def timeRemaining(durations, remainder, method):
    if method == TimeEstimation.Off:
        return 0
    elif method == TimeEstimation.First:
        return durations[0] * remainder
    elif method == TimeEstimation.Last:
        return durations[-1] * remainder
    elif method == TimeEstimation.Minimum:
        return min(durations) * remainder
    elif method == TimeEstimation.Maximum:
        return max(durations) * remainder
    elif method == TimeEstimation.Mean:
        return np.mean(durations) * remainder
    elif method == TimeEstimation.Median:
        return np.median(durations) * remainder


class InterruptableOperation(QDialog):
    def __init__(self, count=None, time_estimation_method=TimeEstimation.Mean,
                 operation='', icon='MISC_empty', parent=None):
        super(InterruptableOperation, self).__init__(parent)
        self.setWindowFlags(Qt.Tool)

        self._operation = operation
        self._count = count
        self._time_estimation_method = time_estimation_method
        self._previous_update = None
        self._durations = []
        self._stop = False

        self.setWindowTitle(operation)
        self.setWindowIcon(ui.icon(icon, 32))

        layout = QGridLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self._icon_label = QLabel()
        if icon and icon != 'MISC_empty':
            self._icon_label.setPixmap(ui.icon(icon, 64).pixmap(64))
        else:
            self._icon_label.setHidden(True)
        layout.addWidget(self._icon_label, 0, 0, -1, 1)

        self._progress_status_label = QLabel('Performing...')
        self._progress_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._progress_status_label, 0, 1, 1, -1)

        self._progress_time_label = QLabel()
        self._progress_time_label.setFont(MONOSPACE_FONT)
        self._progress_time_label.setAlignment(Qt.AlignCenter)
        self._progress_time_label.setToolTip('Elapsed / Remaining')
        layout.addWidget(self._progress_time_label, 1, 1)

        self._progress = QProgressBar()
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(5)
        self._progress.setRange(0, count or 0)
        layout.addWidget(self._progress, 2, 1)

        self.setSizeGripEnabled(False)

    def hideEvent(self, event):
        self._stop = True

    def closeEvent(self, event):
        self._stop = True

    def __enter__(self):
        self.open()
        self._previous_update = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.deleteLater()
        return exc_type == hou.OperationInterrupted

    def updateProgress(self, num=None, status=None):
        if self._stop:
            raise hou.OperationInterrupted

        time_elapsed = timedelta(seconds=int(sum(self._durations)))
        progress = (int(num / float(self._count) * 100) if num and self._count else '~')

        if status is not None:
            self._progress_status_label.setText(status)
            message = '{} (Press Esc to Cancel) {} ({}%)'.format(
                time_elapsed, status, progress
            )
            hou.ui.setStatusMessage(message, hou.severityType.Message)

        if num is None:
            return

        current_time = time()
        self._durations.append(current_time - self._previous_update)
        self._previous_update = current_time

        time_remaining = timedelta(
            seconds=int(timeRemaining(
                self._durations,
                self._count - num,
                self._time_estimation_method
            ))
        )
        self._progress_time_label.setText('{} / {}'.format(time_elapsed, time_remaining))
        if self._count:
            self._progress.setValue(num)

        if status is None:
            message = '{} (Press Esc to Cancel) {} ({}%)'.format(
                time_elapsed, self._operation, progress
            )
            hou.ui.setStatusMessage(message, hou.severityType.Message)

        QApplication.processEvents()
