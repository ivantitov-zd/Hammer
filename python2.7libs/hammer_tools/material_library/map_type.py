from hammer_tools.material_library.db import connect
from hammer_tools.material_library.text import alphaNumericTokens


class MapType(object):
    Unknown = 'unknown'
    Thumbnail = 'thumb'
    Diffuse = 'diff'
    Roughness = 'rough'
    Glossiness = 'gloss'
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
            MapType.Glossiness,
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
            MapType.Glossiness: 'Glossiness',
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
        if not reload and MapType.__labels is not None:
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

    @staticmethod
    def labels(map_type, reload=False):
        if not reload and MapType.__labels is not None and map_type in MapType.__labels:
            return MapType.__labels[map_type]

        with connect() as connection:
            cursor = connection.execute('SELECT label FROM map_types_labels WHERE map_type = :map_type',
                                        {'map_type': map_type})
        labels = tuple(row['label'] for row in cursor.fetchall())
        if MapType.__labels:
            MapType.__labels[map_type] = labels
        return labels

    @staticmethod
    def mapType(name):
        name_tokens = alphaNumericTokens(name.lower())[::-1]
        found_pos = float('+inf')
        found_type = None
        for map_type, tags in MapType.allLabels().items():
            for tag in tags:
                if tag in name_tokens:
                    pos = name_tokens.index(tag)
                    if pos > found_pos:
                        continue
                    elif pos == found_pos:
                        raise AssertionError('Found intersections between tags in different map types.')
                    found_pos = pos
                    found_type = map_type
                    break
        return found_type or MapType.Unknown


DEFAULT_MAP_TYPES_LABELS = {
    MapType.Unknown: (),
    MapType.Thumbnail: ('thumbnail', 'thumb', 'preview'),
    MapType.Diffuse: ('diffuse', 'diff', 'albedo', 'basecolor', 'color'),
    MapType.Roughness: ('roughness', 'rough'),
    MapType.Glossiness: ('glossiness', 'gloss'),
    MapType.Metalness: ('metalness', 'metallic', 'metal'),
    MapType.Reflection: ('reflection', 'refl', 'specular', 'spec'),
    MapType.Refraction: ('refraction', 'refr', 'transparency'),
    MapType.Normal: ('normal', 'norm'),
    MapType.Bump: ('bump',),
    MapType.Subsurface: ('subsurface', 'sss'),
    MapType.Opacity: ('opacity', 'alpha', 'cutout'),
    MapType.Emission: ('emission', 'emissive'),
    MapType.Displacement: ('displacement', 'disp', 'height'),
    MapType.AmbientOcclusion: ('ambientocclusion', 'ambient', 'occlusion', 'ao')
}
