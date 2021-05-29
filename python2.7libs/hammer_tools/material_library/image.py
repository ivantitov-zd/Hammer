try:
    from PyQt5.QtCore import QBuffer, QIODevice
except ImportError:
    from PySide2.QtCore import QBuffer, QIODevice


def imageToBytes(image):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    image.save(buffer, 'png')
    data = buffer.data()
    buffer.close()
    return data
