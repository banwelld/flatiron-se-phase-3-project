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
    get_user_input_std,
    render_header,
    generate_disp_name,
)


# menu option generation

def generate_menu_options(
    option_type: str,
    entity_collection: Union[list, tuple],
    operation_collection: dict,
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
        options = generate_operation_options(operation_collection)

    return tuple(options)


def generate_nav_options(menu_ops_config: dict, nav_config: dict, entity_selected: bool) -> dict:
    """
    Generates a dict of navigational menu options based on the conditions necessary for displaying
    each option.
    
    The exit option is shown, by default, allowing users to end their current session altogether.
    The clear option is shown iff selected_entities contains either a participant or a team. And 
    the back option is shown on menus where the option's visibility depth is equal to or exceeds
    the menu's depth.
    """
    menu_depth = menu_ops_config.get("menu_depth", 2)
    
    options = {}
    
    for option_name, option_config in nav_config.items():
        visibility_depth = option_config["menu_option"]["visibility_depth"]
    
        is_clear = option_config["menu_option"]["return_sentinel"] == "clear"
        is_back = option_config["menu_option"]["return_sentinel"] == "back"
        is_exit = option_config["menu_option"]["return_sentinel"] == "exit"
    
        has_entities =  is_clear and entity_selected
        is_deep_enough = is_back and visibility_depth >= menu_depth
        
        if is_exit or has_entities or is_deep_enough:
            options[option_name] = option_config
    
    return options
    

def generate_participant_options(entity_collection: Union[list, tuple]) -> tuple:
    return (
        {
            "menu_text": generate_disp_name(participant, "option"),
            "selection_item": participant,
        }
        for participant in entity_collection
    )


def generate_team_options(entity_collection: Union[list, tuple]) -> tuple:
    return (
        {
            "menu_text": generate_disp_name(team, "option"),
            "selection_item": team,
        }
        for team in entity_collection
    )


def generate_operation_options(operation_collection: dict) -> tuple:
    return (
        {
            "menu_text": tint_string(
                "option",
                attrs["display"].get(
                    "menu_text",
                    "** No Description Available **",
                ),
            ),
            "selection_item": operation_name,
        }
        for operation_name, attrs in operation_collection.items()
    )


# menu rendering

def render_menu(
    menu_options: Union[tuple, dict, list],
    nav_options: Union[list, tuple],
):
    print_collection(fmt_menu_options(menu_options))
    print()
    print_collection(fmt_nav_options(nav_options))
    print()


# handling user input

def handle_menu_input(menu_options: tuple, nav_options: dict) -> str:
    """
    Solicits and returns a command-line response from a user if it passes validation.
    Warns user that response is invalid and repeats prompt until receiving a valid response.
    """
    close_menu = False
    while not close_menu:
        response = get_user_input_std("Enter your selection: ")

        if response.isdigit() and int(response) >= 0:
            close_menu = validate_num_response(menu_options, response)
        elif isinstance(response, str) and len(response) == 1:
            close_menu = validate_alpha_response(nav_options, response)
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


def validate_alpha_response(nav_options: dict, menu_response: str) -> bool:
    if any(
        (
            menu_response in val["menu_option"]["selectors"]
            for val in nav_options.values()
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
        (
            f"{index:<2} {option['menu_text']}"
            if isinstance(option, dict)
            else f"{index:<2} {option}"
        )
        for index, option in enumerate(menu_options, start=1)
    )


def fmt_nav_options(nav_options: dict) -> tuple:
    return (
        tint_string(
            attrs["menu_option"]["format"],
            generate_nav_option_text(attrs),
        )
        for attrs in nav_options.values()
    )


def generate_nav_option_text(nav_attrs: dict) -> str:
    options_attr = nav_attrs.get("menu_option")
    selector = options_attr.get("selectors")[0].upper()
    display_attr = nav_attrs.get("display")
    menu_text = display_attr.get("menu_text", "TEXT_UNAVAILABLE")
    return f"{selector:<2} {menu_text}"


# main function

def run_menu(
    option_type: str,
    clear_selected_func: callable,
    entity_collection: Union[list, tuple] = None,
    **selected: dict,
) -> Union[type, str, object]:

    operation_config = MENU_OPS_CONFIG.get(option_type)
    operation_collection = OPS_CONFIG

    team = selected.get("team")
    team_name = generate_disp_name(team, "fresh")

    participant = selected.get("participant")
    participant_name = generate_disp_name(participant, "fresh")
    
    entity_selected = participant or team
    
    print("entity_selected: ", entity_selected)
    print(team, participant); input()

    menu_options = generate_menu_options(option_type, entity_collection, operation_collection)
    nav_options = generate_nav_options(operation_config, NAV_OPS_CONFIG, entity_selected)
    
    render_header(
        operation_config,
        participant_name,
        team_name,
        entity_selected,
        ctrl_c_cancel=False,
    )

    render_menu(menu_options, nav_options)

    user_response = handle_menu_input(menu_options, nav_options)

    if user_response.isdigit():
        return process_num_response(menu_options, int(user_response))
    else:
        nav_operation = process_alpha_response(user_response)
        return process_nav_response(nav_operation, clear_selected_func)


if __name__ == "__main__":
    while True:
        print(run_menu("operation"), "WOOT!")
        input()
