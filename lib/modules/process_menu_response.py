import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from util.nav_sentinels import (
    USER_BACK,
    USER_RESET,
    USER_QUIT,
)
from util.warnings import warn_invalid_selection
from util.helpers import get_input_with_prompt


sentinel_map = {
    "back": USER_BACK,
    "reset": USER_RESET,
    "quit": USER_QUIT,
}


def validate_response(
    response: Union[str, int], menu_options: tuple, nav_options: tuple
) -> bool:
    """
    Validates menu responses by compiling lists of the valid numeric and alphabetic
    menu option selectors and compares the user's response to an aggregate list of
    those selectors. If the response is in the list then returns True else warns
    the user and returns False.
    """
    valid_numbers = list(str(num) for num in range(1, len(menu_options) + 1))
    valid_letters = list(option[1][0].lower for option in nav_options)
    if response.lower() in valid_numbers + valid_letters:
        return True
    warn_invalid_selection()
    return False


def main(menu_options: tuple, nav_options: tuple) -> Union[Participant, Team, str, object]:
    """
    Allows the user to input a value and - if the value is a valid menu option
    selector - returns either the team or participant object associated to the
    numeric menu selection or returns the navigation sentinel associated to the
    alphanetic menu selection.
    """
    end_loop = False
    while not end_loop:
        user_response = get_input_with_prompt("Enter your selection: ")
        end_loop = validate_response(user_response, menu_options, nav_options)

    if user_response.isdigit():
        return menu_options[int(user_response) - 1].get("selection_item")
    else:
        selected_option = next(
            (option for option in nav_options if option[0] == user_response)
        )
        return sentinel_map[selected_option]
