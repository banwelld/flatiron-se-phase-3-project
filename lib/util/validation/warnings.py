import os
from typing import Union
from util.text_colour_map import text_colour_map as text_colour


def generate_action_success_message(entity_name: str, action: str) -> str:
    """
    Generates a success message for the specified action on the given item.

    Args:
        entity_name (str)): The entity on which the action was performed.
        action (str): The action performed on the entity.

    Returns:
        success_message (str): The success message.
    """
    action_message = text_colour["oops"](f"{action.upper()}")
    success_message = f"{entity_name} : {action_message}"
    return success_message


def render_success_message(entity_name: str, action: str):
    """
    Displays a success message for a specified entity and action, clears the console,
    and prompts the user to continue.

    Args:
        entity_name (str): The name of the entity involved in the action.
        action (str): The action performed on the entity.
    """
    success_message = generate_action_success_message(entity_name, action)

    os.system("cls" if os.name == "nt" else "clear")

    print(success_message)
    print()
    print()
    input(text_colour["plain"]("Hit <enter> to continue..."))


def render_warning(warning_msg: str):
    """
    Generates a blank screen with a warning message in red. The time
    parameter is required so that the function can determine whether to
    go back to the previous screen on timeout or to render a "press any
    key" message if the user selects 0 seconds.
    """
    print()
    print(text_colour["oops"](warning_msg))
    print()
    print()


def warn_invalid_selection():
    render_warning("Invalid selection. Please try again.")


def warn_invalid_char(display_name: str):
    render_warning(
        f"Invalid {display_name}: Only letters and spaces allowed, plus periods, dashes and apostrophes. Numbers allowed for team names."
    )


def warn_length_invalid(display_name: str, min_length: int, max_length: int):
    render_warning(
        f"Invalid {display_name}: Must contain between {min_length} and {max_length} characters."
    )


def warn_invalid_date_format(display_name: str):
    render_warning(
        f"Invalid {display_name}: YYYY-MM-DD format expected (must have leading zeros)."
    )


def warn_date_invalid(display_name: str):
    render_warning(
        f"Invalid {display_name}: Date does not exist. Check day/month combination."
    )


def warn_team_full():
    render_warning("Selected team is full. Cannot add new participants.")
