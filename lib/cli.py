import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from classes.session_state import SessionState
from modules.run_menu import run_menu
from modules.create_entity import create_entity
from modules.delete_entity import delete_entity
from modules.update_entity import update_entity
from modules.team_assignment import assign_to_team
from modules.get_config import (
    MENU_OPS_CONFIG,
    OPS_CONFIG,
)
from modules.user_sentinels import (
    is_cancelled,
    is_cleared,
)
from util.helpers import (
    render_result_screen,
    generate_disp_name,
    render_header,
)
from strings.user_messages import NONE_SELECTED

# load all teams

Team.fetch_all()
    
# constants

MODEL_TYPES = tuple((key for key, val in MENU_OPS_CONFIG.items() if val.get("option_type") == "model"))

COMPETING_TEAMS = tuple((t for t in Team.all if not t.is_free_agents))

FREE_AGENT_TEAM = next((t for t in Team.all if t.is_free_agents), None)


# session state

selected_entities = SessionState(**{key: None for key in MODEL_TYPES})

participants_loaded = SessionState(**{str(team.id): False for team in Team.all})


# league operations

def create_team() -> str:
    
    team = create_entity(Team)
    if is_cancelled(team): return
    
    selected_entities.set("team", team)

    return generate_disp_name(team)


def create_participant() -> str:
    team = selected_entities.get("team")
    
    participant = create_entity(Participant)
    if is_cancelled(participant): return participant
    
    result = assign_to_team(participant, team, do_confirm=False)
    if is_cancelled(result): return

    selected_entities.set("participant", participant)    
    
    return generate_disp_name(participant)


def recruit_free_agent() -> str:
    team = selected_entities.get("team")
    participant = selected_entities.get("participant")
    
    ensure_participants_loaded(FREE_AGENT_TEAM)
    
    result = assign_to_team(participant, team, FREE_AGENT_TEAM)
    if is_cancelled(result): return
    
    return generate_disp_name(participant)


def remove_participant() -> str:
    team = selected_entities.get("team")
    participant = selected_entities.get("participant")
    
    ensure_participants_loaded(FREE_AGENT_TEAM)

    result = assign_to_team(participant, FREE_AGENT_TEAM, team)
    if is_cancelled(result): return
    
    return generate_disp_name(participant)


def delete_team() -> str:
    team = selected_entities.get("team")
    team_name = generate_disp_name(team)
    
    ensure_participants_loaded(FREE_AGENT_TEAM)

    result = delete_entity(team, FREE_AGENT_TEAM)
    if is_cancelled(result): return
    
    return team_name


def delete_participant() -> str:
    participant = selected_entities.get("participant")
    participant_name = generate_disp_name(participant)
    
    result = delete_entity(participant)
    if is_cancelled(result): return
    
    return participant_name


def update_participant_first_name() -> str:
    participant = selected_entities.get("participant")
    
    result = update_entity(participant, "first_name")
    if is_cancelled(result): return
    
    return generate_disp_name(participant)


def update_participant_last_name() -> str:
    participant = selected_entities.get("participant")
    
    result = update_entity(participant, "last_name")
    if is_cancelled(result): return
    
    return generate_disp_name(participant)


def update_team_name() -> str:
    team = selected_entities.get("team")
        
    result = update_entity(team, "name")
    if is_cancelled(result): return
    
    return generate_disp_name(team)


# utility functions

def ensure_entity_loaded(model_type: str, selection_list: list) -> Union[Participant, Team]:
    if entity := selected_entities.get(model_type):
        return entity
    
    entity = run_menu(model_type, selection_list, **selected_entities.data)
    
    if is_cancelled(entity):
        return entity
        
    selected_entities.set(model_type, entity)        
        
    return entity


def select_from_teams() -> Team:
    """
    Run the menu for selecting a competing team and lazy load participants to team.
    """
    selected_team = run_menu("team", COMPETING_TEAMS)
    ensure_participants_loaded(selected_team)
    return selected_team


def select_from_participants(team: Team) -> Participant:
    """
    Run the menu for selecting a participant from a team.
    """
    selected_participant = run_menu("participant", team.participants)
    return selected_participant


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

def reset_selected_entities_if_cleared(entity: Union[Participant, Team]) -> None:
    if is_cleared(entity):
        selected_entities.reset()


# Runner function for the entire application

def main():
    """
    Main function to run the operations menu.
    """
    team = NONE_SELECTED
    participant = NONE_SELECTED
    
    exit_menu = False    
    while not exit_menu:
        # run the main menu as the backbone of the application
        selection = run_menu("operation", **selected_entities.data)
        reset_selected_entities_if_cleared(selection)
        
        if is_cancelled(selection): continue

        # if operation requires a team, ensure that selected_entities has one
        if OPS_CONFIG[selection].get("resolve_team"):
            team = ensure_entity_loaded("team", COMPETING_TEAMS)
            reset_selected_entities_if_cleared(team)
            
            if is_cancelled(team): continue

            # lazy load a team's members when it's been selected
            ensure_participants_loaded(team)
            
        # if operation requires a participant, ensure that selected_entities has one
        if OPS_CONFIG[selection].get("resolve_participant"):
            participant = ensure_entity_loaded("participant", team.participants)
            reset_selected_entities_if_cleared(participant)
            
            if is_cancelled(participant): continue
        
        print(selection); input()
            
        # Execute the selected operation
        operation = globals().get(selection)
        render_header(OPS_CONFIG.get(selection), generate_disp_name(participant), generate_disp_name(team), ctrl_c_cancel=True)
        result = operation()
        
        # Render success screen
        render_result_screen(result, selection)
            
        # clear selected entities based on the operational config settings
        if OPS_CONFIG[selection].get("retain_sel_team") is False:
            selected_entities.set("team", None)
        
        if OPS_CONFIG[selection].get("retain_sel_participants") is False:
            selected_entities.set("participant", None)
        
        
if __name__ == "__main__":
    main()