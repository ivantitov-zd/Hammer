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
