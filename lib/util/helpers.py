import os
from typing import Union
from models.participant import Participant
from models.team import Team
from modules.get_config import OPS_CONFIG
from modules.user_sentinels import (
    USER_CANCEL,
    USER_CLEAR,
)
from strings.tint_string import tint_string
from strings.display_messages import (
    HIT_ENTER,
    APP_TITLE,
    NONE_SELECTED,
    CANCEL_INSTRUCTION,
    OP_CANCELLED,
)


# helper functions


def get_action_msg(operation_name: str) -> str:
    return OPS_CONFIG[operation_name]["display"].get(
        "action_message", "ACTION_MESSAGE_NOT_AVAILABLE"
    )


def print_collection(collection: Union[list, tuple], new_line_after: bool = True):
    for item in collection:
        print(item)
    if new_line_after:
        print()


def fmt_participant_name(first_name: str, last_name: str) -> str:
    if first_name is None or last_name is None:
        return ""
    return f"{last_name.upper()}, {first_name}"


def clear_cli():
    os.system("cls" if os.name == "nt" else "clear")


def generate_title(text: str) -> str:
    formatted_text = "" if not text else f" - {text}"
    title = f"*** {APP_TITLE}{formatted_text} ***"
    return title


def get_user_input_std(prompt_text: str) -> str:
    return input(tint_string("ask", f"\n{prompt_text}"))


def get_model_type(entity: Union[Participant, Team]) -> str:
    return type(entity).__name__.lower()


def find_entity_in_list(entities: list, entity_id: int) -> Union[Participant, Team]:
    return next((e for e in entities if e.id == entity_id), None)


def generate_success_msg(disp_name: str, operation: str) -> str:
    action_msg = get_action_msg(operation)
    action_clause = tint_string("oops", f"{action_msg.upper()}")
    message = f"{disp_name} : {action_clause}"
    return message


def generate_disp_text(
    text_or_entity: Union[Participant, Team, str, None], tint_name: str = "fresh"
) -> str:
    result = NONE_SELECTED
    if isinstance(text_or_entity, Participant):
        participant_name = fmt_participant_name(
            text_or_entity.first_name, text_or_entity.last_name
        )
        result = tint_string(tint_name, participant_name)
    elif isinstance(text_or_entity, Team):
        result = tint_string(tint_name, text_or_entity.name)
    elif isinstance(text_or_entity, str) and text_or_entity != NONE_SELECTED:
        result = tint_string(tint_name, text_or_entity)

    return result


def process_nav_response(
    response: str, clear_selected_func: callable
) -> Union[object, None]:
    """
    Returns quit_program() if the entity is the EXIT_SENTINEL.
    Clears the selected entities if the entity is the CLEAR_SENTINEL.
    Returns the USER_CANCEL_SENTINEL if the entity is not the EXIT_SENTINEL.
    """
    from modules.quit_program import quit_program

    if response == "exit":
        return quit_program()

    elif response == "clear":
        clear_selected_func()
        return USER_CLEAR

    else:
        return USER_CANCEL


# cli rendering functions


def render_header(
    operation_name: str,
    instruction: str,
    participant_name: str = None,
    team_name: str = None,
    entity_selected: bool = True,
    ctrl_c_cancel: bool = True,
) -> None:
    clear_cli()

    render_title(operation_name)

    if ctrl_c_cancel:
        print(CANCEL_INSTRUCTION)
        print("\n")

    if entity_selected:
        render_selected_entities_table(
            participant_name or NONE_SELECTED, team_name or NONE_SELECTED
        )

    if instruction:
        render_instruction(instruction)


def render_title(operation_name: str):
    title = generate_title(operation_name).upper()
    print(tint_string("title", title.upper()))
    print(tint_string("title", "=" * len(title)))
    print()


def render_instruction(instruction: str, color_key: str = "plain"):
    print(tint_string(color_key, instruction))
    print()


def render_selected_entities_table(participant_name: str, team_name: str):
    line = "-" * 50
    print(f"{tint_string('prompt', 'CURRENTLY SELECTED')}")
    print(f"{tint_string('prompt', line)}")
    if participant_name != "None Selected":
        print(f"{tint_string('prompt', 'Participant:')} {participant_name}")
        print(f"{tint_string('prompt', line)}")
    if team_name != NONE_SELECTED:
        print(f"{tint_string('prompt', 'Team:')} {team_name}")
        print(f"{tint_string('prompt', line)}")
    print()


def render_result_screen(entity_name: str, operation: str):
    """
    Clears the console and displays a standardized success message for a specified
    entity and action and prompts the user to continue.
    """
    if isinstance(entity_name, str):
        message = generate_success_msg(entity_name, operation)
    else:
        message = OP_CANCELLED

    clear_cli()

    print(message)
    print()
    input(tint_string("plain", HIT_ENTER))


def render_warning(warning_msg: str, enter_to_continue: bool = False):
    """
    Generates standardized warning messages to user in "oops" yellow from provided text.
    """
    print()
    print(tint_string("oops", warning_msg))
    print("\n")
    if enter_to_continue:
        input(tint_string("plain", HIT_ENTER))
