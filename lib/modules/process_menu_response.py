import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Participant, Team
from config import OPS_CONFIG
from util.warnings import (
    warn_invalid_selection,
    warn_team_empty,
    warn_team_full,
)
from util.helpers import get_input_with_prompt


def ensure_valid_selection(
    response: Union[str, int], menu_options: tuple, nav_options: tuple
) -> bool:
    valid_numbers = list(option[0] for option in menu_options)
    valid_letters = list(option[0].lower() for option in nav_options)
    if response.lower() in valid_numbers + valid_letters:
        return True
    warn_invalid_selection()
    return False


def ensure_team_not_full(team: Team, participant_count: int) -> bool:
    if team is None and participant_count is None:
        return True
    max_size = team.CONFIG["max_team_participants"]
    if 0 <= participant_count < max_size:
        return True
    warn_team_full()
    return False


def ensure_team_not_empty(participant_count: int) -> bool:
    if participant_count is None:
        return True
    if participant_count > 0:
        return True
    warn_team_empty()
    return False


def validate_response(
    response: str,
    menu_options: tuple,
    nav_options: tuple,
    team: Team,
    participant_count: int,
) -> bool:
    is_valid_selection = ensure_valid_selection(response, menu_options, nav_options)

    if not is_valid_selection:
        return False

    menu_option = next(
        (option for option in menu_options if option[0] == response), None
    )

    if not menu_option:
        return is_valid_selection

    if not isinstance(menu_option[2], str):
        return is_valid_selection

    operation = menu_option[2]
    is_valid_participant_count = True

    if OPS_CONFIG[operation].get("verify_team_full"):
        is_valid_participant_count = ensure_team_not_full(team, participant_count)
    elif OPS_CONFIG[operation].get("verify_team_empty"):
        is_valid_participant_count = ensure_team_not_empty(participant_count)

    return is_valid_selection and is_valid_participant_count


def main(
    menu_options: tuple,
    nav_options: tuple,
    team: Team = None,
    participant_count: int = None,
    **sentinels: dict,
) -> Union[Participant, Team, str, object]:
    """
    Allows the user to input a value. If the value is a valid menu option
    selector and - in the case of operation selection - if the selected team's
    participant count aligns with the needs of the operation, returns either the
    team or participant object associated to the numeric menu selection or returns
    the navigation sentinel associated to the alphanetic menu selection.
    """
    end_loop = False
    while not end_loop:
        user_response = get_input_with_prompt("Enter your selection: ").lower()
        end_loop = validate_response(
            user_response, menu_options, nav_options, team, participant_count
        )

    all_options = list(menu_options) + list(nav_options)
    selected_option = next(
        (option for option in all_options if option[0].lower() == user_response)
    )

    if user_response.isdigit():
        return selected_option[2]
    else:
        return sentinels[selected_option[2]]
