from datetime import datetime
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


def enforce_free_agent_team_id_1(team: type):
    team_name = team.name
    team_id = team.id

    try:
        assert team_id == 1

    except AssertionError:
        raise AssertionError(
            f"Team '{team_name}' has incorrect id. Expected 1, got {team_id}. Database must be re-initialised and re-seeded"
        )

def ensure_team_not_full(team: type) -> bool:
    try:
         return enforce_range(len(team.participants), 0, team.CONFIG["participants"]["validation"]["max_list_length"])
                
    except ValueError:
        return False