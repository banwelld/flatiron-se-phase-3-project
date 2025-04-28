import json
from pathlib import Path
from typing import Union, Type, Any
from classes.session_state import SessionState
from config.old.operation_config import CONFIG as OPS_CONFIG
from models.team import Team
from models.participant import Participant
from modules.get_confirmation import get_confirmation
from modules.warnings import (
    render_result_screen,
)
from util.validation.enforcers import (
    enforce_in_list,
)

# open text color map (rgb values) for reading

color_map_path = Path(__file__).parent / "text_color_map.json"

with color_map_path.open("r", encoding="utf-8") as c:
    COLOR_MAP = json.load(c)

# cancellation sentinel

USER_CANCELLATION = object()

# function mapping for primary operations


# validation collections

MENU_TYPES = (
    key.replace("select_", "") for key, value in OPS_CONFIG.items() if value["is_menu"]
)

MODEL_TYPES = ("participant", "team")

# fetch all teams from database

Team.fetch_all()

# instantiate state objects

entities_selected = SessionState(**{model: None for model in MODEL_TYPES})
members_loaded_by_team = SessionState(**{str(team.id): False for team in Team.all})
menus_open = SessionState(**{menu: False for menu in MENU_TYPES})

# primary operations


def perform_operation(operation_name: str) -> Union[Type, None]:
    """
    Executes a series of operations based on the provided operation name.
    The function enforces that the operation_name is valid, sets the
    execution flow for the given operation, and then executes each
    operation in the flow by calling the corresponding action function.

    Args:
        operation_name (str): The name of the operation to perform.

    Returns:
        completed (bool): True if the operation was completed successfully,
                          False otherwise. An incomplete operation indicates
                          that the user selected the "Return to main menu
                          and clear selected" option.
    """
    if operation_name is None:
        return

    enforce_in_list(operation_name, *OPS_CONFIG.keys())

    execution_order: tuple = generate_exec_order(operation_name)

    for operation in execution_order:
        dependency = operation != operation_name
        result = run_exec_operation(operation, dependency)
        if result is USER_CANCELLATION:
            return USER_CANCELLATION


def assign_team_id(participant: Participant, team: Team):
    if participant is not None:
        setattr(participant, "team_id", team.id)
        participant.update()


def add_free_agent_to_team(esc_sentinel: object):
    """
    Adds a free agent to a team via the participant menu
    """
    if not get_confirmation("Add the selected player to the selected team?"):
        return esc_sentinel

    assign_team_id(entities_selected.get("participant"), entities_selected.get("team"))
    display_name = generate_entity_display_name(entities_selected.get("participant"))
    render_result_screen(
        display_name, OPS_CONFIG["add_free_agent_to_team"]["display"]["action_message"]
    )


def return_to_main_menu():
    entities_selected.reset()
    return USER_CANCELLATION


# operation aux functions


def run_exec_operation(operation: str, is_dependency: bool) -> None:
    if is_dependency:
        result = perform_operation(operation)
    else:
        result = OPS_FUNCS[operation]()

    return result


def add_item_to_selected(selection_item: Any):
    data_type = type(selection_item).__name__.lower()

    if data_type in MODEL_TYPES:
        entities_selected.set(data_type, selection_item)


# UI rendering


def render_exit_salutation():
    print()
    print(COLOR_MAP["fresh"]("Goodbye!"))
    print()
    print()


# utility functions


def generate_exec_order(operation_name: str) -> list:
    """
    Generates a list of operations (dependencies and main operation) based upon the execution
    order in the operations map for the given operation.

    Args:
        operation_name (str): The name of the operation for which to generate the execution list.

    Returns:
        exec_order (tuple): An ordered tuple of operations to be executed.
    """
    deps = OPS_CONFIG[operation_name]["dependency_order"]

    if deps is None:
        return (operation_name,)

    sorted_keys = [
        key
        for key, _ in sorted(deps.items(), key=lambda item: item[1])
        if deps[key] > 0
    ]
    pre_ops = [
        key
        for key in sorted_keys
        if OPS_CONFIG[key]["is_dependency"] and OPS_CONFIG[key]["is_pre_op"]
    ]
    post_ops = [
        key
        for key in sorted_keys
        if OPS_CONFIG[key]["is_dependency"] and not OPS_CONFIG[key]["is_pre_op"]
    ]

    exec_order = tuple(pre_ops + [operation_name] + post_ops)
    return exec_order


def generate_participant_team_name_combo(participant_name: str, team_name: str) -> str:
    """
    Creates a formatted display name for a participant, including their team name.

    Args:
        participant_name (str): The participant name to be formatted.
        team_name (str): The participant's team's name.

    Returns:
        display_name (str): The formatted display name for the participant.
    """
    if not team_name:
        return participant_name
    team_name_formatted = COLOR_MAP["nope"](team_name)
    open_paren = COLOR_MAP["fresh"]("(")
    close_paren = COLOR_MAP["fresh"](")")
    return f"{participant_name} {open_paren}{team_name_formatted}{close_paren}"


def get_loaded_team_participants(team_id: int) -> list:
    return [p for p in Participant.all.values() if p.team_id == team_id]


def fetch_team_participants(team_id: int) -> list:
    members_loaded_by_team.set(team_id, True)
    return Participant.fetch_all(team_id)


def get_team_participants(team_id: int) -> list:
    if members_loaded_by_team.get(team_id):
        return get_loaded_team_participants(team_id)
    else:
        return fetch_team_participants(team_id)
