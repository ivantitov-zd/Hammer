import os
import re


class TextureFormat(object):
    __slots__ = ('_compression_ext', '_license_ext', '_extension')

    @staticmethod
    def wrap(*extensions):
        return tuple(TextureFormat(ext) for ext in extensions)

    def __init__(self, name):
        name, ext = os.path.splitext(name)

        if not ext:
            ext = name

        if ext.lower() in {'.z', '.gz', '.sc', '.bz2'}:
            self._compression_ext = ext
            _, ext = os.path.splitext(name)
        else:
            self._compression_ext = ''

        if ext.lower().endswith(('nc', 'lc')):
            self._license_ext = ext
            ext = ext[:-2]
        else:
            self._license_ext = ''

        self._extension = ext.lstrip('.')

    def __eq__(self, other):
        if not other:
            return False

        if isinstance(other, str):
            if set(other).intersection({'*', '\\', '[', ']', '|'}):
                return bool(re.match(other, self._extension.lower()))
            else:
                return self._extension.lower() == other.lstrip('.').lower()
        elif isinstance(other, TextureFormat):
            return self._extension.lower() == other._extension.lower()
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._extension.lower())

    def __repr__(self):
        return self._extension.lower()

    def __str__(self):
        return '.' + self._extension + self._license_ext + self._compression_ext
