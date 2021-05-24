from ..db import connect


class MapType(object):
    Unknown = 0
    Thumbnail = 1
    Diffuse = 2
    Roughness = 3
    Metalness = 4
    Reflection = 5
    Refraction = 6
    Normal = 7
    Bump = 8
    Subsurface = 9
    Opacity = 10
    Emission = 11
    Displacement = 12
    AmbientOcclusion = 13

    __tags = None

    @staticmethod
    def all():
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
    def name(map_type):
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
    def tags():
        if MapType.__tags is not None:
            return MapType.__tags

        with connect() as connection:
            cursor = connection.execute('SELECT * FROM map_type_tag')

            tags = {map_type: [] for map_type in MapType.all()}

            for data in cursor.fetchall():
                map_type = data['map_type']
                tag = data['tag']
                tags[map_type].append(tag)

            MapType.__tags = {map_type: tuple(tags) for map_type, tags in tags.items()}
            return MapType.__tags


DEFAULT_MAP_TYPE_TAGS = {
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
