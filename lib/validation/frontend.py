import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from validation.enforcers import (
    enforce_range,
    enforce_valid_chars,
    enforce_valid_date,
)
from util.warnings import (
    warn_length_invalid,
    warn_invalid_char,
    warn_date_invalid,
    warn_invalid_date_format,
)


def validate_name(attr_config: dict, check_val: str):

    range_floor = attr_config["validation"]["min_length"]
    range_cieling = attr_config["validation"]["max_length"]

    try:
        enforce_range(len(check_val), range_floor, range_cieling)
        enforce_valid_chars(check_val, attr_config["validation"]["regex"])

        return True

    except ValueError:
        warn_length_invalid()
        return False
    except NameError:
        warn_invalid_char()
        return False


def validate_date(attr_config: dict, check_val: str):
    try:
        enforce_valid_date(check_val, attr_config["validation"]["regex"])
        return True

    except RuntimeError:
        warn_invalid_date_format()
        return False
    except ValueError:
        warn_date_invalid()
        return False
