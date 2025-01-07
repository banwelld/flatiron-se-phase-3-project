def validate_string(item, min_length, max_length):
    if not isinstance(item, str):
        raise ValueError(wrong_type_msg(str, item))
    if not min_length <= len(item) <= max_length:
        raise ValueError(
            f"'{item}' not within allowed length parameters (expected: "
            f"'{min_length} - {max_length}', actual: '{len(item)}')"
        )
    return True


def wrong_type_msg(item, type):
    return (
        f"Property is of wrong type (expected: '{type(type)}', actual: "
        f"'{type(item)}')"
    )