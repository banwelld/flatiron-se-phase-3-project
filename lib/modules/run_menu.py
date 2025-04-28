import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.get_config import (
    OPS_CONFIG,
    MENU_OPS_CONFIG,
    NAV_OPS_CONFIG,
)
from modules.warnings import warn_invalid_selection
from validation.enforcers import enforce_range
from strings.tint_string import tint_string
from util.helpers import (
    process_nav_response,
    print_collection,
    fmt_participant_name,
    get_user_input_std,
    render_header,
    generate_disp_name,
)
from strings.user_messages import NONE_SELECTED


# menu option generation

def generate_menu_options(
    option_type: str,
    entity_collection: Union[list, tuple],
    ops_collection: dict,
) -> tuple:
    """
    Generates and returns a tuple of menu options based on the provided option
    type and collection.
    """
    if option_type == "participant":
        options = generate_participant_options(entity_collection)

    elif option_type == "team":
        options = generate_team_options(entity_collection)

    elif option_type == "operation":
        options = generate_operation_options(ops_collection)

    return tuple(options)


def generate_participant_options(entity_collection: Union[list, tuple]) -> tuple:
    return (
        {
            "menu_text": fmt_participant_name(
                participant.first_name,
                participant.last_name,
            ),
            "selection_item": participant,
        }
        for participant in entity_collection
    )


def generate_team_options(entity_collection: Union[list, tuple]) -> tuple:
    return (
        {
            "menu_text": team.name,
            "selection_item": team,
        }
        for team in entity_collection
    )


def generate_operation_options(ops_collection: dict) -> tuple:
    return (
        {
            "menu_text": attrs["display"].get(
                "menu_text", "** No Description Available **"
            ),
            "selection_item": operation_name,
        }
        for operation_name, attrs in ops_collection.items()
    )


# menu rendering

def render_menu(
    menu_options: Union[tuple, dict, list],
    nav_options: Union[list, tuple],
    menu_depth: int,
    display_all_options: bool = False,
):
    print_collection(fmt_menu_options(menu_options))
    print()
    print_collection(fmt_nav_options(nav_options, menu_depth, display_all_options))
    print()


# handling user input


def handle_menu_input(menu_depth: int, options: tuple, display_all_options: bool) -> str:
    """
    Solicits and returns a command-line response from a user if it passes validation.
    Warns user that response is invalid and repeats prompt until receiving a valid response.
    """
    close_menu: bool = False
    while not close_menu:
        response = get_user_input_std("Enter your selection: ")

        if response.isdigit() and int(response) >= 0:
            close_menu = validate_num_response(options, response)
        elif isinstance(response, str) and len(response) == 1:
            close_menu = validate_alpha_response(response, menu_depth, display_all_options)
        else:
            warn_invalid_selection()

    return response


# validating user input

def validate_num_response(options: tuple, response: str) -> bool:
    try:
        enforce_range(int(response), 1, len(list(options)))
        return True
    except ValueError:
        warn_invalid_selection()
        return False


def validate_alpha_response(menu_response: str, menu_depth: int, display_all_options: bool) -> bool:
    if any(
        (
            menu_response in val["menu_option"]["selectors"]
            for val in NAV_OPS_CONFIG.values()
            if menu_depth >= val["menu_option"]["visibility_depth"] or display_all_options
        )
    ):
        return True
    else:
        warn_invalid_selection()
        return False


# processing user input

def process_num_response(options: tuple, menu_response: int) -> Union[type, str]:
    """
    Returns the selections selection_item attribute
    """
    selection = options[menu_response - 1]  # - 1 to align to 0 index value
    return selection.get("selection_item")


def process_alpha_response(menu_response: str) -> Union[str, None]:
    """
    Returns the sentinel name ("back", "clear", "exit") associated with the menu
    response.
    """
    selector_to_sentinel = {
        selector: attrs["menu_option"].get("return_sentinel")
        for attrs in NAV_OPS_CONFIG.values()
        for selector in attrs["menu_option"]["selectors"]
    }
    return selector_to_sentinel.get(menu_response)


# utility functions

def fmt_menu_options(menu_options: dict) -> tuple:
    return (
        tint_string(
            "option",
            (
                f"{index:<2} {option['menu_text']}"
                if isinstance(option, dict)
                else f"{index:<2} {option}"
            ),
        )
        for index, option in enumerate(menu_options, start=1)
    )


def fmt_nav_options(nav_options: dict, menu_depth: int, display_all_options: bool) -> tuple:
    return (
        tint_string(
            attrs["menu_option"]["format"],
            generate_nav_option_text(attrs),
        )
        for attrs in nav_options.values()
        if menu_depth >= attrs["menu_option"]["visibility_depth"] or display_all_options
    )


def generate_nav_option_text(nav_attrs: dict) -> str:
    options_attr = nav_attrs.get("menu_option")
    selector = options_attr.get("selectors")[0].upper()
    display_attr = nav_attrs.get("display")
    menu_text = display_attr.get("menu_text", "TEXT_UNAVAILABLE")
    return f"{selector:<2} {menu_text}"


# runner function

def run_menu(
    option_type: str,
    entity_collection: Union[list, tuple] = None,
    **selected: dict,
) -> Union[type, str, object]:
    
    show_selected_and_clear_option = selected.get("participants") is not None or selected.get("team") is not None

    operation_config = MENU_OPS_CONFIG.get(option_type)
    nav_options = NAV_OPS_CONFIG
    ops_collection = OPS_CONFIG

    menu_depth = operation_config.get("menu_depth")
    menu_options = generate_menu_options(option_type, entity_collection, ops_collection)
    
    team = selected.get("team", NONE_SELECTED)
    team_name = generate_disp_name(team, "fresh")
    
    participant = selected.get("participant", NONE_SELECTED)
    participant_name = generate_disp_name(participant, "fresh")
       
    render_header(operation_config, participant_name, team_name, show_selected_and_clear_option, ctrl_c_cancel=False)

    render_menu(menu_options, nav_options, menu_depth, show_selected_and_clear_option)

    user_response = handle_menu_input(menu_depth, menu_options, show_selected_and_clear_option)

    if user_response.isdigit():
        return process_num_response(menu_options, int(user_response))
    else:
        nav_operation = process_alpha_response(user_response)
        return process_nav_response(nav_operation)


if __name__ == "__main__":
    while True:
        print(run_menu("operation"), "WOOT!")
        input()
