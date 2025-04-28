import os
from typing import Union
from models.participant import Participant
from models.team import Team
from modules.get_config import OPS_CONFIG
from modules.user_sentinels import USER_CANCEL, USER_CLEAR
from strings.tint_string import tint_string
from strings.user_messages import (
    HIT_ENTER,
    APP_TITLE,
    NONE_SELECTED,
    CANCEL_INSTRUCTION,
)


# helper functions

def get_action_msg(operation_name: str) -> str:
    return (
        OPS_CONFIG.get(operation_name, "OP_NOT_FOUND")
        .get("display", "NO_DISP_ATTR")
        .get("action_message", "NO_MESSAGE")
    )


def print_collection(collection: Union[list, tuple]):
    for item in collection:
        print(item)


def fmt_participant_name(first_name: str, last_name: str, tint_name: str = "plain") -> str:
    if first_name is None or last_name is None:
        return ""
    return tint_string(tint_name, f"{last_name.upper()}, {first_name}")


def clear_cli():
    os.system("cls" if os.name == "nt" else "clear")


def generate_title(text: str) -> str:
    formatted_text = "" if not text else f" - {text}"
    title = f"*** {APP_TITLE}{formatted_text} ***"
    return title


def get_user_input_std(prompt_text: str) -> str:
    return input(tint_string("ask", f"\n{prompt_text}"))


def get_model_type(model: Union[Participant, Team]) -> str:
    return model.__name__.lower()


def find_entity_in_list(entities: list, entity_id: int) -> Union[Participant, Team]:
    return next((e for e in entities if e.id == entity_id), None)


def generate_success_msg(disp_name: str, operation: str) -> str:
    """
    Generates a success message for the specified action on the given item.
    """
    action_msg = get_action_msg(operation)
    action_clause = tint_string("oops", f"{action_msg.upper()}")
    message = f"{disp_name} : {action_clause}"
    return message


def generate_disp_name(entity: Union[Participant, Team, str, None], tint_name: str = "fresh") -> str:
    if isinstance(entity, Participant):
        entity_name = fmt_participant_name(entity.first_name, entity.last_name, tint_name)
    elif isinstance(entity, Team):
        entity_name = tint_string(tint_name, entity.name)
    elif isinstance(entity, str):
        entity_name = tint_string(tint_name, entity)
    elif entity is None:
        entity_name = NONE_SELECTED

    if entity_name == "None Selected":
        return tint_string("oops", entity_name)
    return entity_name


def process_nav_response(response: str) -> Union[object, None]:
    """
    Returns quit_program() if the entity is the EXIT_SENTINEL.
    Clears the selected entities if the entity is the CLEAR_SENTINEL.
    Returns the USER_CANCEL_SENTINEL if the entity is not the EXIT_SENTINEL.
    """
    from modules.quit_program import quit_program
    
    if response == "exit":
        return quit_program()

    elif response == "clear":
        return USER_CLEAR

    else:
        return USER_CANCEL


# cli rendering functions

def render_header(
    operation_config: dict,
    participant_name: str = None,
    team_name: str = None,
    display_selected: bool = True,
    ctrl_c_cancel: bool = True
) -> None:
    clear_cli()
    
    display_config = operation_config.get("display", {})
    
    render_title(display_config.get("title", ""))

    if display_selected:
        render_selected_entities_table(participant_name or NONE_SELECTED, team_name or NONE_SELECTED)
    if prompt := display_config.get("screen_prompt", False):
        render_instruction(prompt)
    if ctrl_c_cancel:
        render_instruction(f"({CANCEL_INSTRUCTION})", "nope")


def render_title(text: str = ""):
    title = generate_title(text)
    print(tint_string("title", title.upper()))
    print(tint_string("title", "=" * len(title)))
    print()


def render_instruction(instruction: str, color_key: str = "plain"):
    print(tint_string(color_key, instruction))
    print()


def render_selected_entities_table(participant_name: str, team_name: str):
    line = ("-" * 55)
    print(f"{tint_string('prompt', 'CURRENTLY SELECTED')}")
    print(f"{tint_string('prompt', line)}")
    print(f"{tint_string('prompt', 'Participant:'):>13} {participant_name}")
    print(f"{tint_string('prompt', line)}")
    print(f"{tint_string('prompt', 'Team:'):>13} {team_name}")
    print(f"{tint_string('prompt', line)}")
    print()


def render_result_screen(entity_name: str, operation: str):
    """
    Clears the console and displays a standardized success message for a specified
    entity and action and prompts the user to continue.
    """
    message = generate_success_msg(entity_name, operation) if isinstance(entity_name, str) else OP_CANCELLED

    clear_cli()

    print(message)
    print()
    print()
    input(tint_string("plain", HIT_ENTER))


def render_warning(warning_msg: str):
    """
    Generates standardized warning messages to user in "oops" yellow from provided text.
    """
    print()
    print(tint_string("oops", warning_msg))
    print()
    print()