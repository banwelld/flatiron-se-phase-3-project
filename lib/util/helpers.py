import os
from typing import Union
from models.participant import Participant
from models.team import Team
from config.get_config import OPS_CONFIG
from strings.tint_string import tint_string
from strings.display_messages import (
    HIT_ENTER,
    APP_TITLE,
    NONE_SELECTED,
    CANCEL_INSTRUCTION,
    OP_CANCELLED,
)


def clear_cli():
    os.system("cls" if os.name == "nt" else "clear")


def generate_disp_text(
    str_or_entity: Union[Participant, Team, str], tint_name: str = "fresh"
) -> str:
    """
    Takes in a string, a participant, or a team and returns a formatted version of the
    string or the entity name for display in the CLI. Participant names are formatted
    as "LAST, First", while team names and strings receive no positional formatting. 
    """
    arg_type_map = {
        "participant": tint_string(tint_name, f"{str_or_entity.last_name.upper()}, {str_or_entity.first_name}"),
        "team": tint_string(tint_name, str_or_entity.name),
        "str": tint_string(tint_name, str_or_entity)
    }
    return arg_type_map.get(type(str_or_entity).__name__, NONE_SELECTED)


def get_input_with_prompt(prompt_text: str) -> str:
    return input(generate_disp_text(f"\n{prompt_text}"), "ask")


def render_menu(menu_options: tuple, nav_options: tuple):
    """
    Concatenates the provided option collections into a list with an empty string
    separating the menu options for the nav options. Prints all options formatted
    with selectors (op[0]) preceding option descriptions (op[1]), leaving a blank
    line (empty string) between the option types with the help of the empty string.
    """
    all_options = list(menu_options) + [""] + list(nav_options)
    for op in all_options:
        print(op if isinstance(op, str) else f"{op[0]:<2} {op[1]}")


def render_header(
    operation_name: str,
    instruction: str,
    participant_name: str = None,
    team_name: str = None,
    ctrl_c_cancel: bool = True,
) -> None:
    clear_cli()

    # render the page title with the operation name as a suffix to the app name
    title_text = f"*** {APP_TITLE.upper()} - {operation_name.upper()} ***"
    print(generate_disp_text(title_text, "title"))
    print(f"{generate_disp_text('=' * len(title_text))}\n\n", 'title')

    # conditionally render header components if they're needed
    if ctrl_c_cancel:
        print(f"{CANCEL_INSTRUCTION}\n\n")
    if participant_name or team_name:
        print(f"{generate_disp_text('CURRENTLY SELECTED', 'prompt')}")
        print(f"{generate_disp_text('-' * 50, 'prompt')}")
    if participant_name:
        print(f"{generate_disp_text('Participant:', 'prompt'):>12} {participant_name}")
        print(f"{generate_disp_text('-' * 50, 'prompt')}")
    if team_name:
        print(f"{generate_disp_text('Team:', 'prompt'):>12} {team_name}")
        print(f"{generate_disp_text('-' * 50, 'prompt')}")
    if instruction:
        print(f"{generate_disp_text(instruction, "plain")}\n\n")


def render_result_screen(entity_disp_name: str, operation_name: str):
    """
    Clears the console and displays a standardized success message for a specified
    entity and action and prompts the user to continue.
    """
    if isinstance(entity_disp_name, str):
        # append the operation's action message to the entity's display name
        success_str = OPS_CONFIG[operation_name].get("success_msg")
        success_disp_str = generate_disp_text(f"{success_str.upper()}", "oops")
        message = f"{entity_disp_name} : {success_disp_str}"
    else:
        op_disp_name = generate_disp_text(operation_name, "option")
        cancel_disp_str = generate_disp_text(OP_CANCELLED, "oops")
        message = f"{op_disp_name} : {cancel_disp_str}"

    clear_cli()
    print(f"{message}\n\n")
    input(generate_disp_text(HIT_ENTER, "plain"))
    

def render_warning(warning_msg: str, enter_to_continue: bool = False):
    """
    Generates standardized warning messages to user in "oops" yellow from provided text.
    """
    print(f"\n{generate_disp_text(warning_msg, 'oops')}\n\n")
    if enter_to_continue:
        input(generate_disp_text(HIT_ENTER, "plain"))


def render_team_participant_list(state: dict):
    print(generate_disp_text(f"{state['team'].upper()} PARTICIPANTS\n\n", "ask"))
    for p in state["team_participants"]:
        print(generate_disp_text(p), "option")
    print("\n")
