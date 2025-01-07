import re
from datetime import date


def within_limits(number: int, min_limit: int, max_limit: int) -> None:
    return min_limit <= number <= max_limit


def valid_date_format(date_str: str) -> bool:
    pattern = r"^[0-9]{4}/[0-9]{2}/[0-9]{2}$"
    match = re.match(pattern, date_str)
    return match is not None


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
            f"Date '{date_str}' format is invalid, expected 'YYYY/MM/DD'"
        )
        
    if not valid_date_value(date_str):
        raise ValueError(
            f"Date '{date_str}' value is invalid (check month/day combination)"
        )


def validate_object(item, expected_type: type) -> None:
    if not isinstance(item, expected_type):
        raise ValueError(
            f"Object '{item}' type is invalid, expected "
            f"'{expected_type.__name__}', but got '{type(item).__name__}'"
        )


def validate_name(name: str, max_length: int):
    if not within_limits(len(name), 2, max_length):
        raise ValueError(
            f"Name '{name}' length is invalid, expected between 2 and "
            f"{max_length} characters, but got {len(name)}"
        )
        
    pattern = r"[^a-zA-Z '.\-]"
    match = re.match(name, pattern)
    if match is None:
        raise ValueError(
            f"Name '{name}' contains invalid character '{match.group()}', "
            "only letters, periods (.), hyphens (-), and apostrophes (') "
            "are allowed"
        )