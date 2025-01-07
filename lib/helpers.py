import re
from datetime import date


def within_limits(number: int, min_limit: int, max_limit: int) -> None:
    return min_limit <= number <= max_limit


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


def validate_object(item, expected_type: type) -> None:
    if not isinstance(item, expected_type):
        raise ValueError(
            f"Expected type '{expected_type.__name__}', but got "
            f"'{type(item).__name__}' for value '{item}'"
        )

        
def validate_with_limits(
    item: str | int, 
    expected_type: type, 
    min_limit: int, 
    max_limit: int
) -> None:

    if not isinstance(min_limit, int) or not isinstance(max_limit, int):
        raise TypeError("Both 'min_limit' and 'max_limit' must be integers")
    
    if min_limit > max_limit:
        raise ValueError("'min_limit' cannot be greater than 'max_limit'")
    
    validate_object(item, expected_type)

    if isinstance(item, str):
        validated_value = len(item)
        property_name = "length"
    elif isinstance(item, int):
        validated_value = item
        property_name = "value"
    else:
        raise TypeError(
            f"Unsupported type '{type(item).__name__}'. Expected 'str' or 'int'."
        )
    
    if not within_limits(validated_value, min_limit, max_limit):
        raise ValueError(
            f"Expected {property_name} between {min_limit} and {max_limit}, "
            f"but got {validated_value}"
            + (f" for '{item}'" if property_name == "length" else "")
        )