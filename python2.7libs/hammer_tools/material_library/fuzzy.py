def fuzzyMatch(pattern, text):
    if pattern == text:
        return True

    index = 0
    try:
        for char in text:
            if char == pattern[index]:
                index += 1
    except IndexError:
        pass

    return index == len(pattern)


def fuzzyMatchWeight(pattern, text):
    try:
        pos_weight = 1 - text.index(pattern[0]) / 1000.0
    except ValueError:
        return 0

    pattern_length = len(pattern)

    if pattern in text:
        return pattern_length * pattern_length + pos_weight

    max_weight = 0
    start_index = 0
    text_length = len(text)
    while start_index != text_length:
        current_index = start_index
        prev_token_pos = -1
        weight = 0
        count = 0
        first_token = True
        try:
            first_token_pos = text.index(pattern[0], start_index)
        except ValueError:
            break

        for token in pattern:
            try:
                pos = text.index(token, current_index)
            except ValueError:
                break
            if pos == prev_token_pos + 1 or first_token:
                first_token = False
                count += 1
            else:
                weight += count * count
                count = 1
            prev_token_pos = pos
            current_index = pos + 1

        weight += count * count

        if weight > max_weight:
            max_weight = weight

        start_index = first_token_pos + 1

    return max_weight + pos_weight
