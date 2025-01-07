import re
from datetime import date


def valid_str_length(item: str, max_str_length: int) -> None:
    return 1 <= len(item) <= max_str_length


def valid_date_format(date_str: str) -> bool:
    pattern = r"[0-9]{4}/[0-9]{2}/[0-9]{2}"
    regex = re.compile(pattern)
    return regex.fullmatch(date_str) is not None


def valid_date_value(date_str: str) -> bool:
    date_yr = int(date_str[:4])
    date_mon = int(date_str[5:7])
    date_day = int(date_str[8:])
    
    try:
        date(date_yr, date_mon, date_day)
        return True
    except ValueError:
        return False


def validate_date(date_str: str) -> None:
    if not valid_date_format(date_str):
        raise ValueError(
            "Date incorrectly formatted (expected: 'YYYY/MM/DD', got: "
            f"'{date_str}')"
        )
        
    if not valid_date_value(date_str):
        raise ValueError(
            "Invalid date value (check month and day combination)"
        )


def validate_type(
    item,
    expected_type: type,
    max_str_length: int = None,
) -> None:
    if not isinstance(item, expected_type):
        raise ValueError(
            f"Expected type '{expected_type.__name__}', but got "
            f"'{type(item).__name__}' for value '{item}'"
        )

    if (isinstance(item, str) and
            max_str_length is not None and
            not valid_str_length(item, max_str_length)):
        raise ValueError(
            f"Expected length of '1 - {max_str_length}', but got "
            f"'{len(item)}' for string '{item}'"
        )