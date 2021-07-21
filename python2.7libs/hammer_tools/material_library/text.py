import os
import re

try:
    from PyQt5.QtGui import QFont
except ImportError:
    from PySide2.QtGui import QFont

MONOSPACE_FONT = QFont('Monospace')
MONOSPACE_FONT.setStyleHint(QFont.Monospace)

NOT_ALNUM_PATTERN = re.compile(r'[\W_\s]')
SPACE_SEQUENCES_PATTERN = re.compile(r'\s+')


def alphaNumericTokens(text):
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


def convertName(name, options):  # Todo: Rewrite with args
    remove_prefix = options.get('remove_prefix')
    if remove_prefix and name.startswith(remove_prefix):
        name = name[len(remove_prefix):]

    remove_suffix = options.get('remove_suffix')
    if remove_suffix and name.endswith(remove_suffix):
        name = name[:-len(remove_suffix)]

    chars_to_replace_with_spaces = options.get('chars_to_replace_with_spaces')
    if chars_to_replace_with_spaces:
        if '*' in chars_to_replace_with_spaces:
            name = re.sub(NOT_ALNUM_PATTERN, ' ', name)

        if chars_to_replace_with_spaces != '*':
            name = re.sub('[' + re.escape(chars_to_replace_with_spaces) + ']', ' ', name)

    if options.get('remove_repeated_spaces'):
        name = re.sub(SPACE_SEQUENCES_PATTERN, ' ', name)

    if options.get('switch_case'):
        case = options.get('new_case')
        if case is None:
            raise ValueError('Key "new_case" not found.')

        name_with_original_case = name

        if case == 0:  # Title
            name = name.title()
        elif case == 1:  # Sentence
            name = name.capitalize()
        elif case == 2:  # Lower
            name = name.lower()
        elif case == 3:  # Upper
            name = name.upper()
        else:
            raise ValueError('Invalid case.')

        if options.get('keep_words_in_all_caps'):
            name = ''.join(min(c1, c2) for c1, c2 in zip(name_with_original_case, name))

    return name.strip()
