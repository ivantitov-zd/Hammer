import os

try:
    from PyQt5.QtGui import QImage, QPixmap, QIcon
except ImportError:
    from PySide2.QtGui import QImage, QPixmap, QIcon
import requests

from ..material import Material
from .library import Library


class PolyHavenMaterial(Material):
    def __init__(self, asset_id, name):
        super(PolyHavenMaterial, self).__init__()

        self._asset_id = asset_id
        self._name = name

    def id(self):
        return self._asset_id

    def thumbnail(self, engine=None, reload=False):
        if not self._thumbnail or reload:
            cache_path = os.path.join('D:/polyhaven_cache', self._asset_id)
            if not os.path.exists(cache_path):
                resp = requests.get('https://cdn.polyhaven.com/asset_img/thumbs/{}.png?height=256'
                                    .format(self._asset_id))
                with open(cache_path, 'wb') as file:
                    file.write(resp.content)
            self._thumbnail = QIcon(QPixmap(cache_path))
        return self._thumbnail

    def textures(self):
        return ()

    def path(self):
        return 'https://polyhaven.com/a/' + self._asset_id


class PolyHavenLibrary(Library):
    def __init__(self):
        super(PolyHavenLibrary, self).__init__()
        if not os.path.exists('D:/polyhaven_cache'):
            raise IOError

        self._name = 'Poly Haven'
        self._comment = 'Materials from PolyHaven.com'
        self._favorite = True

        self._assets = requests.get('https://api.polyhaven.com/assets?t=textures').json()

    def materials(self):
        return tuple(PolyHavenMaterial(asset_id, self._assets[asset_id]['name']) for asset_id in self._assets)

    def textures(self):
        return ()

    def path(self):
        return 'https://polyhaven.com/textures'
