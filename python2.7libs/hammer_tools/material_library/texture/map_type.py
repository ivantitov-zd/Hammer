from ..db import connect


class MapType(object):
    Unknown = 'unknown'
    Thumbnail = 'thumb'
    Diffuse = 'diff'
    Roughness = 'rough'
    Metalness = 'metal'
    Reflection = 'refl'
    Refraction = 'refr'
    Normal = 'normal'
    Bump = 'bump'
    Subsurface = 'sss'
    Opacity = 'opacity'
    Emission = 'emission'
    Displacement = 'disp'
    AmbientOcclusion = 'ao'

    __labels = None

    @staticmethod
    def allTypes():
        return (
            MapType.Unknown,
            MapType.Thumbnail,
            MapType.Diffuse,
            MapType.Roughness,
            MapType.Metalness,
            MapType.Reflection,
            MapType.Refraction,
            MapType.Normal,
            MapType.Bump,
            MapType.Subsurface,
            MapType.Opacity,
            MapType.Emission,
            MapType.Displacement,
            MapType.AmbientOcclusion
        )

    @staticmethod
    def typeName(map_type):
        return {
            MapType.Unknown: 'Unknown',
            MapType.Thumbnail: 'Thumbnail',
            MapType.Diffuse: 'Diffuse',
            MapType.Roughness: 'Roughness',
            MapType.Metalness: 'Metalness',
            MapType.Reflection: 'Reflection',
            MapType.Refraction: 'Refraction',
            MapType.Normal: 'Normal',
            MapType.Bump: 'Bump',
            MapType.Subsurface: 'Subsurface',
            MapType.Opacity: 'Opacity',
            MapType.Emission: 'Emission',
            MapType.Displacement: 'Displacement',
            MapType.AmbientOcclusion: 'Ambient Occlusion'
        }[map_type]

    @staticmethod
    def allLabels(reload=False):
        if MapType.__labels is not None and not reload:
            return MapType.__labels

        with connect() as connection:
            cursor = connection.execute('SELECT * FROM map_types_labels')

            labels = {map_type: [] for map_type in MapType.allTypes()}

            for data in cursor.fetchall():
                map_type = data['map_type']
                label = data['label']
                labels[map_type].append(label)

            MapType.__labels = {map_type: tuple(labels) for map_type, labels in labels.items()}
            return MapType.__labels


DEFAULT_MAP_TYPES_LABELS = {
    MapType.Unknown: (),
    MapType.Thumbnail: ('thumbnail', 'thumb', 'preview'),
    MapType.Diffuse: ('diffuse', 'diff', 'albedo', 'basecolor', 'color'),
    MapType.Roughness: ('roughness', 'rough', 'glossiness', 'gloss'),
    MapType.Metalness: ('metalness', 'metallic', 'metal'),
    MapType.Reflection: ('reflection', 'refl', 'specular', 'spec'),
    MapType.Refraction: ('refraction', 'refr', 'transparency'),
    MapType.Normal: ('normal', 'norm'),
    MapType.Bump: ('bump', 'height'),
    MapType.Subsurface: ('subsurface', 'sss'),
    MapType.Opacity: ('opacity', 'alpha', 'cutout'),
    MapType.Emission: ('emission', 'emissive'),
    MapType.Displacement: ('displacement', 'disp'),
    MapType.AmbientOcclusion: ('ambientocclusion', 'ambient', 'occlusion', 'ao')
}
