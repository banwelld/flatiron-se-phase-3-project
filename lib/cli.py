import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from classes.session_state import SessionState
from lib.modules.process_menu_response import main as run_menu
from modules.create_entity import main as create_entity
from lib.modules.delete_entity_prep import main as delete_entity
from modules.update_entity import main as update_entity
from modules.team_assignment import main as assign_to_team
from config.get_config import (
    MENU_OPS_CONFIG,
    OPS_CONFIG,
)
from lib.util.nav_sentinels import is_cancelled
from util.helpers import (
    render_result_screen,
    generate_disp_text,
    render_header,
)
from strings.display_messages import NONE_SELECTED


# load all teams

Team.fetch_all()


# constants

MODEL_TYPES = tuple(
    (key for key, val in MENU_OPS_CONFIG.items() if val.get("option_type") == "model")
)

FREE_AGENT_TEAM = next((t for t in Team.all if t.is_free_agents), None)


# session state

selected_entities = SessionState(**{key: None for key in MODEL_TYPES})

participants_loaded = SessionState(**{str(team.id): False for team in Team.all})


# league operations


def create_team() -> str:
    selected_entities.reset()

    team = create_entity(Team)
    if is_cancelled(team):
        return

    selected_entities.set("team", team)

    return generate_disp_text(team)


def create_participant() -> str:
    selected_entities.set("participant", None)
    team = selected_entities.get("team")

    participant = create_entity(Participant)
    if is_cancelled(participant):
        return participant

    result = assign_to_team(participant, team, do_confirm=False)
    if is_cancelled(result):
        return

    selected_entities.set("participant", participant)

    return generate_disp_text(participant)


def recruit_free_agent() -> str:
    team = selected_entities.get("team")
    participant = selected_entities.get("participant")

    result = assign_to_team(participant, team, FREE_AGENT_TEAM)
    if is_cancelled(result):
        return

    return generate_disp_text(participant)


def remove_participant() -> str:
    team = selected_entities.get("team")
    participant = selected_entities.get("participant")

    result = assign_to_team(participant, FREE_AGENT_TEAM, team)
    if is_cancelled(result):
        return

    return generate_disp_text(participant)


def delete_team() -> str:
    selected_entities.set("participant", None)

    team = selected_entities.get("team")
    team_name = generate_disp_text(team)

    result = delete_entity(team, FREE_AGENT_TEAM)
    if is_cancelled(result):
        return

    return team_name


def delete_participant() -> str:
    participant = selected_entities.get("participant")
    participant_name = generate_disp_text(participant)

    result = delete_entity(participant)
    if is_cancelled(result):
        return

    return participant_name


def update_participant_first_name() -> str:
    participant = selected_entities.get("participant")

    result = update_entity(participant, "first_name")
    if is_cancelled(result):
        return

    return generate_disp_text(participant)


def update_participant_last_name() -> str:
    participant = selected_entities.get("participant")

    result = update_entity(participant, "last_name")
    if is_cancelled(result):
        return

    return generate_disp_text(participant)


def update_team_name() -> str:
    selected_entities.set("participant", None)
    team = selected_entities.get("team")

    result = update_entity(team, "name")
    if is_cancelled(result):
        return

    return generate_disp_text(team)


# utility functions


def get_sorted_comp_teams(team_list: list) -> list:
    """
    Generates, alphabetically sorts and returns a list of
    all competing teams, disregarding the free agent team.
    """
    comp_teams = [t for t in team_list if not t.is_free_agents]
    return sorted(comp_teams, key=lambda t: t.name)


def get_sorted_participants(participant_list: list) -> list:
    """
    Generates, alphabetically sorts and returns a list of
    players in the supplied participant_list argument, sorted
    by last_name and then by first_name.
    """
    return sorted(participant_list, key=lambda p: (p.last_name, p.first_name))


def ensure_entity_loaded(
    model_type: str,
    operation_name: str,
    selection_list: list,
    clear_selected_func: callable,
) -> Union[Participant, Team]:
    if selected_entity := selected_entities.get(model_type):
        return selected_entity

    entity = run_menu(
        model_type,
        clear_selected_func,
        selection_list,
        operation_name,
        **selected_entities.data,
    )

    if is_cancelled(entity):
        return entity

    selected_entities.set(model_type, entity)

    return entity


def ensure_participants_loaded(team: Team) -> None:
    """
    Load the participants for the given team if they haven't been
    loaded already. Updates state to indicate that the participants
    have been loaded.
    """
    if participants_loaded.get(str(team.id)):
        return

    team.fetch_participants()
    participants_loaded.set(str(team.id), True)


def run_operation(
    operation_func: callable,
    operation_name: str,
    instruction: str,
    participant_disp_name: str,
    team_disp_name: str,
    is_cancelable: bool = True,
) -> any:
    participant_selected = participant_disp_name != NONE_SELECTED
    team_selected = team_disp_name != NONE_SELECTED

    participant_or_team_in_state = participant_selected or team_selected

    render_header(
        operation_name,
        instruction,
        participant_disp_name,
        team_disp_name,
        participant_or_team_in_state,
        is_cancelable,
    )
    return operation_func()


# control flow


def main():
    """
    Main function to run the operations menu.
    """
    exit_menu = False
    while not exit_menu:

        operational_team = None
        operational_participant = None

        # run the main menu as the backbone of the application
        selection = run_menu(
            "operation", selected_entities.reset, **selected_entities.data
        )
        if is_cancelled(selection):
            continue

        # unpack operations config to variables
        selection_config = OPS_CONFIG[selection]
        operation_name = selection_config.get("title_suffix", "")

        # if operation requires a team, ensure that selected_entities has one
        if selection_config.get("resolve_team"):
            competing_teams = get_sorted_comp_teams(Team.all)

            prospective_team = ensure_entity_loaded(
                "team", operation_name, competing_teams, selected_entities.reset
            )
            if is_cancelled(prospective_team):
                continue

            operational_team = prospective_team

            # lazy load a team's members when it's been selected
            ensure_participants_loaded(operational_team)

        # ensure the free agents are loaded if the operation's config requires it
        if selection_config.get("load_free_agents"):
            ensure_participants_loaded(FREE_AGENT_TEAM)

        # if operation requires a participant, ensure that selected_entities has one
        if selection_config.get("resolve_participant"):
            selected_team_members = get_sorted_participants(
                operational_team.participants
            )
            free_agents = get_sorted_participants(FREE_AGENT_TEAM.participants)

            participant_list = (
                free_agents
                if selection == "recruit_free_agent"
                else selected_team_members
            )

            prospective_participant = ensure_entity_loaded(
                "participant", operation_name, participant_list, selected_entities.reset
            )
            if is_cancelled(prospective_participant):
                continue

            operational_participant = prospective_participant

        # Execute the selected operation
        operation_func = globals().get(selection)

        participant_name = (
            generate_disp_text(operational_participant)
            if operational_participant
            else NONE_SELECTED
        )
        team_name = (
            generate_disp_text(operational_team) if operational_team else NONE_SELECTED
        )

        result = run_operation(
            operation_func,
            operation_name,
            selection_config.get("instruction", ""),
            participant_name,
            team_name,
        )

        # Render success screen
        render_result_screen(result, selection)

        # clear selected entities based on the operational config settings
        if OPS_CONFIG[selection].get("retain_sel_team") is False:
            selected_entities.set("team", None)

        if OPS_CONFIG[selection].get("retain_sel_participant") is False:
            selected_entities.set("participant", None)


if __name__ == "__main__":
    main()
