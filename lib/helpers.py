import re
from datetime import date

def validate_string(item, min_length, max_length) -> None:
    if not isinstance(item, str):
        raise ValueError(wrong_type_msg(str, item))
    if not min_length <= len(item) <= max_length:
        raise ValueError(
            f"'{item}' not within allowed length parameters (expected: "
            f"'{min_length} - {max_length}', actual: '{len(item)}')"
        )

def valid_date_format(date_str: str) -> bool:
    pattern = r"[0-9]{2}/[0-9]{2}/[0-9]{4}"
    regex = re.compile(pattern)
    valid_date = regex.fullmatch(date_str)
    return True if valid_date else False

def valid_date_value(date_str: str) -> bool:
    test_year = int(date_str[:4])
    test_month = int(date_str[5:7])
    test_day = int(date_str[8:])
    try:
        if date(test_year, test_month, test_day):
            return True
    except ValueError:
        return False

def validate_date(item: str) -> None:
    if not valid_date_format(item):
        raise ValueError(
            "Date incorrectly formatted (expected: 'YYYY/MM/DD', actual: "
            f"'{item}')"
        )
    if not valid_date_value(item):
        raise ValueError("Invalid month/day combination")

def wrong_type_msg(item, type) -> None:
    return (
        f"Property is of wrong type (expected: '{type(type)}', actual: "
        f"'{type(item)}')"
    )