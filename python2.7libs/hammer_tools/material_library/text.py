import os
import re


def splitAlphaNumeric(text):
    parts = []

    buffer = ''
    for char in text:
        if char.isalnum():
            buffer += char
        elif buffer:
            parts.append(buffer)
            buffer = ''

    if buffer:
        parts.append(buffer)

    return tuple(parts)


def replaceByPattern(file_path, tag, pattern):
    pattern = '(?P<pre>.*?)' + pattern + '(?P<post>.+)'
    path, name = os.path.split(file_path)
    if not re.match(pattern, name):
        return file_path
    name = re.sub(pattern, r'\g<pre>%s\g<post>' % tag, name)
    return path + '/' + name


def replaceUDIM(file_path, tag='%(UDIM)d'):
    return replaceByPattern(file_path, tag, r'(?P<UDIM>10\d{2})')


def replaceUVTile(file_path, tag='%(UVTILE)d'):
    return replaceByPattern(file_path, tag, r'(?P<UVTILE>[uU]\d+_[vV]\d+)')


def replaceUTile(file_path, tag='%(U)d'):
    return replaceByPattern(file_path, tag, r'(?P<UTile>[uU]\d+)')


def replaceVTile(file_path, tag='%(V)d'):
    return replaceByPattern(file_path, tag, r'(?P<VTile>[vV]\d+)')
