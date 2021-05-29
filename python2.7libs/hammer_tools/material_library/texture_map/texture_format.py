import os


class TextureFormat(object):
    __slots__ = ('_compression_ext', '_license_ext', '_extension')

    def __init__(self, name):
        name, ext = os.path.splitext(name)

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
        if isinstance(other, str):
            return self._extension.lower() == other.lstrip('.').lower()
        elif isinstance(other, TextureFormat):
            return self._extension.lower() == other._extension.lstrip('.').lower()
        else:
            return NotImplemented

    def __repr__(self):
        return '.' + self._extension + self._license_ext + self._compression_ext

    def __hash__(self):
        return hash(self._extension)
