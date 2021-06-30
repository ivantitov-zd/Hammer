import re

NOT_ALNUM_PATTERN = re.compile(r'[\W_\s]')
SPACE_SEQUENCES_PATTERN = re.compile(r'\s+')


def convertName(name, options):
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

    return name.strip()
