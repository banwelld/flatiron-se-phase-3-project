import os
import sys
from typing import Union
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Participant, Team
from config import TEXT_COLOR_MAP
from strings.display_messages import (
    HIT_ENTER,
    APP_TITLE,
    NONE_SELECTED,
    CANCEL_INSTRUCTION,
    OP_CANCELLED,
    YN_PROMPT,
)


def fetch_teams():
    all_teams = Team.fetch()
    comp_teams = list(t for t in all_teams if not t.is_free_agents)
    free_team = next((t for t in all_teams if t.is_free_agents), None)
    return (comp_teams, free_team)


def clear_cli():
    os.system("cls" if os.name == "nt" else "clear")


def tint_string(color_key: str, text_string: str) -> str:
    rgb_combo = TEXT_COLOR_MAP[color_key]
    return f"\x1b[38;2;{rgb_combo}m{text_string}\x1b[0m"


def fmt_participant_name(first: str, last: str):
    return f"{last.upper()}, {first}"


def step_back(context: object):
    if context.can_go_back():
        context.pop()
    else:
        context.restart()


def back_to_op_select(
    context: object, team_menu_func: callable, op_menu_func: callable
):
    init_state = context.init_state.copy()
    op_sel_state = context.init_state.copy()
    op_sel_state["team"] = context.state["team"]
    op_sel_state["team_name"] = context.state["team_name"]
    op_sel_state["team_roster"] = (
        context.state["team_roster"] if context.state["team_roster"] else []
    )
    op_sel_state["comp_teams"] = context.state["comp_teams"]
    op_sel_state["free_team"] = context.state["free_team"]
    context.stack.clear()
    context.stack.append((team_menu_func, init_state))
    context.stack.append((op_menu_func, op_sel_state))


def resolve_sentinel(response: object, context: object = None, **sentinels):
    if response is sentinels["back"]:
        return step_back(context)
    elif response is sentinels["reset"]:
        return context.restart()
    elif response is sentinels["quit"]:
        return context.stack.clear()


def generate_disp_text(
    str_or_entity: Union[Participant, Team, str], color_key: str = "name"
) -> str:
    """
    Takes in a string, a participant, or a team and returns a formatted version of the
    string or the entity name for display in the CLI. Participant names are formatted
    as "LAST, First", while team names and strings receive no positional formatting.
    """
    arg_type_map = {
        "participant": lambda: tint_string(
            color_key,
            fmt_participant_name(str_or_entity.f_name, str_or_entity.l_name),
        ),
        "team": lambda: tint_string(color_key, str_or_entity.name),
        "str": lambda: tint_string(color_key, str_or_entity),
    }
    arg_type = type(str_or_entity).__name__.lower()
    return (
        arg_type_map.get(arg_type)()
        if arg_type in arg_type_map.keys()
        else NONE_SELECTED
    )


def get_input_with_prompt(prompt_text: str, tint_decription: str = "ask") -> str:
    response = input(generate_disp_text(f"\n{prompt_text}", tint_decription))
    return response


def get_user_confirmation(prompt: str) -> bool:
    from util.warnings import warn_invalid_selection

    print(f"{prompt}\n")
    exit_loop = False
    while not exit_loop:
        response = get_input_with_prompt(YN_PROMPT, "warn").lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            warn_invalid_selection()


def render_menu(menu_options: tuple, nav_options: tuple):
    """
    Concatenates the provided option collections into a list with an empty string
    separating the menu options for the nav options. Prints all options formatted
    with selectors (op[0]) preceding option descriptions (op[1]), leaving a blank
    line (empty string) between the option types with the help of the empty string.
    """
    fmt_menu_options = ((option[0], option[1], "menu") for option in menu_options)
    fmt_nav_options = (
        (option[0].upper(), option[1], option[3]) for option in nav_options
    )

    all_options = list(fmt_menu_options) + [""] + list(fmt_nav_options)

    for op in all_options:
        print(
            op
            if isinstance(op, str)
            else generate_disp_text(f"{op[0]:>2} {op[1]}", op[2])
        )


def render_header(
    operation_name: str,
    instruction: str,
    participant_name: str = None,
    team_name: str = None,
    team_roster: list = None,
    ctrl_c_cancel: bool = True,
) -> None:
    def draw_table_line():
        print(f"{generate_disp_text('-' * 50, 'prompt')}")

    clear_cli()

    # render the page title with the operation name as a suffix to the app name
    title_text = f"*** {APP_TITLE.upper()} - {operation_name.upper()} ***"
    print(generate_disp_text(title_text, "title"))
    print(f"{generate_disp_text('=' * len(title_text), 'title')}\n")

    # conditionally render header components if they're needed
    if ctrl_c_cancel:
        print(f"{generate_disp_text(CANCEL_INSTRUCTION, 'reset')}\n\n")
    if participant_name or team_name:
        print(f"{generate_disp_text('CURRENTLY SELECTED', 'prompt')}")
        draw_table_line()
    if participant_name:
        print(f"{generate_disp_text('Participant:', 'prompt')} {participant_name}")
        draw_table_line()
    if team_name:
        print(f"{generate_disp_text('Team:', 'prompt')} {team_name}")
        draw_table_line()
    if team_name and team_roster is not None:
        print(f"{generate_disp_text('Team Roster:', 'prompt')}")
        if len(team_roster):
            for p in team_roster:
                print(f"{generate_disp_text(p):>20}")
        else:
            print(generate_disp_text("** Team Empty **", "warn"))
        draw_table_line()
    if instruction:
        print(f"\n{generate_disp_text(instruction, 'plain')}\n")


def render_result(success_msg: str, is_confirmed: bool = True):
    """
    Renders a standardized success message for a specified entity and operation
    and prompts the user to continue.
    """
    print(f"\n\n{success_msg if is_confirmed else OP_CANCELLED}\n\n")
    input(generate_disp_text(HIT_ENTER, "plain"))


def render_warning(warning_msg: str, enter_to_continue: bool = False):
    """
    Generates standardized warning messages to user in "warn" yellow from provided text.
    """
    print(f"\n{generate_disp_text(warning_msg, 'warn')}\n\n")
    if enter_to_continue:
        input(generate_disp_text(HIT_ENTER, "plain"))
