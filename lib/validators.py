import re
from datetime import date


def within_limits(number: int, min_limit: int, max_limit: int) -> bool:
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
            f"Date '{date_str}' format is invalid, expected 'YYYY/MM/DD'")
        
    if not valid_date_value(date_str):
        raise ValueError(
            f"Date '{date_str}' is invalid (check month/day combination)")


def validate_object(item, expected_type: type) -> None:
    if not isinstance(item, expected_type):
        raise ValueError(
            f"Object '{item}' type is invalid, expected "
            f"'{expected_type.__name__}', but got '{type(item).__name__}'")


def validate_name(name: str, max_length: int):
    trimmed_name = " ".join(name.split())
    if not within_limits(len(trimmed_name), 2, max_length):
        raise ValueError(
            f"Name '{trimmed_name}' length is invalid, expected between 2 and "
            f"{max_length} characters, but got {len(trimmed_name)}")
        
    pattern = r"[^a-zA-Z '.\-]"
    match = re.match(trimmed_name, pattern)
    if match is not None:
        raise ValueError(
            f"Name '{trimmed_name}' contains invalid character "
            f"'{match.group()}', only letters, periods (.), hyphens (-), "
            "and apostrophes (') are allowed")
        
        
def validate_int_value(value: int, max_limit: int):
    if not within_limits(int(value), 0, max_limit):
        raise ValueError(
            f"Integer '{value}' is out of range, expected <= {max_limit}")


def validate_captain(team_id, captain_id):
    from models.member import Member
    captain = Member.fetch_by_id(captain_id)
    
    if not captain:
        raise ValueError(
            f"No record in 'members' table having id '{captain_id}'")
        
    if not captain.team_id == team_id:
        raise ValueError(
            "Member/team mismatch: Member belongs to team having id "
            f"'{captain.team_id}', not '{team_id}'")
        
    
