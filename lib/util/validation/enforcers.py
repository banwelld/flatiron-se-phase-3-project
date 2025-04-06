from datetime import datetime
from typing import Dict, Union
from models.participant.model import Participant
from models.team.model import Team
import re


def enforce_range(check_val: int, lower_lim: int, upper_lim: int):
    """
    Validates that check_val is an integer and lies within the inclusive
    range from lower_lim to upper_lim.
    """
    if not lower_lim <= check_val <= upper_lim:
        raise ValueError(
            f"'{check_val}' is out of range. Expected between "
            f"{lower_lim} and {upper_lim}."
        )
    else:
        return True


def enforce_valid_chars(check_val: str, validation_regex: str):
    """
    Validates that check_val does not contain any characters that match
    the supplied regex pattern
    """
    if invalid_char_set := {char for char in re.sub(validation_regex, "", check_val)}:
        invalid_char_str = f"' , ".join(invalid_char_set)
        raise NameError(
            f"'{check_val}' contains invalid character(s): " f"'{invalid_char_str}'."
        )
    else:
        return True


def enforce_valid_date(check_val: str, validation_regex: str):
    """
    Ensures that check_val has valid date formatting (YYYY-MM-DD) and
    then ensures that the date has a valid date value by attempting to
    apply the striptime() method of the datetime class.
    """
    valid_format = re.match(validation_regex, check_val)
    if not valid_format:
        raise RuntimeError(f"'{check_val}' format invalid. Expected 'YYYY-MM-DD'.")
    try:
        datetime.strptime(check_val, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError(f"'{check_val}' is not a valid date.")


def enforce_in_list(item: any, *option_list: any) -> bool:
    if item not in option_list:
        option_string = " or ".join([f"'{option}'" for option in option_list])
        raise ValueError(f"Invalid item. Got '{item}', expected {option_string}.")
    return True


def enforce_no_selection_overwrite(
    operation_name: str, selected: Dict[str, Union[Participant, Team]]
) -> bool:
    """
    Determines whether the selection of an entity should be suppressed based on the operation name
    and the current selection state of the corresponding entity.
    Args:
        operation_name (str): The name of the operation being performed.
        selected (Dict[str, Union[Participant, Team]]): A dictionary containing the current selection
            state, where keys are model names and values are the selected entities (e.g., Participant
            or Team instance).
    Returns:
        bool: Returns False if the operation name is "select_operation". Otherwise, returns True if
        the entity corresponding to the operation name is already selected, and False otherwise.
    """
    if operation_name == "select_operation":
        return False

    is_selected = selected.get(operation_name) is not None

    return is_selected
