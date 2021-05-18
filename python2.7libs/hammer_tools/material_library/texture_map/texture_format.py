import os


class TextureFormat(object):
    def __init__(self, name):
        name, ext = os.path.splitext(name)
        if ext.lower() in ('.z', '.gz', '.sc', 'bz2'):
            _, _ext = os.path.splitext(name)
            ext = _ext + ext
        self._extension = ext.lstrip('.')

    def __eq__(self, other):
        if isinstance(other, str):
            return self._extension.lower() == other.lstrip('.').lower()
        elif isinstance(other, TextureFormat):
            return self._extension.lower() == other._extension.lstrip('.').lower()
        else:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, str):
            return other + '.' + self._extension
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return other + '.' + self._extension
        else:
            return NotImplemented

    def __repr__(self):
        return '.' + self._extension
