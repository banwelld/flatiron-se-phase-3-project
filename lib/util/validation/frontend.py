from util.validation.enforcers import (
    enforce_range,
    enforce_valid_chars,
    enforce_valid_date,
)
from util.validation.warnings import (
    warn_length_invalid,
    warn_invalid_char,
    warn_date_invalid,
    warn_invalid_date_format,
)


def validate_name(display_name: str, attrib_config: dict, check_val: str):

    range_floor = attrib_config["validation"]["min_length"]
    range_cieling = attrib_config["validation"]["max_length"]

    try:
        enforce_range(len(check_val), range_floor, range_cieling)
        enforce_valid_chars(check_val, attrib_config["validation"]["regex"])

        return True

    except ValueError:
        warn_length_invalid(display_name, range_floor, range_cieling)
        return False
    except NameError:
        warn_invalid_char(display_name)
        return False


def validate_date(display_name: str, attrib_config: dict, check_val: str):
    try:
        enforce_valid_date(check_val, attrib_config["validation"]["regex"])
        return True

    except RuntimeError:
        warn_invalid_date_format(display_name)
        return False
    except ValueError:
        warn_date_invalid(display_name)
        return False


def is_valid_response(display_name: str, attrib_config: dict, input_text: str):
    data_type = attrib_config["validation"]["validate_as"]
    if input_text == "!!":
        return True
    elif data_type == "name":
        return validate_name(display_name, attrib_config, input_text)
    elif data_type == "date":
        return validate_date(display_name, attrib_config, input_text)
    else:
        return True
