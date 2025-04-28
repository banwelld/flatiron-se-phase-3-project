import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from modules.get_confirmation import get_confirmation
from modules.team_assignment import reassign_all_participants
from modules.user_sentinels import USER_CANCEL
from util.helpers import get_model_type


# runner_function

def delete_entity(entity: Union[Participant, Team], destination_team: Team = None):
    """
    Confirms user's intent and deletes the selected entity of the specified model
    type with confirmation. If user cancels, sends the back sentinel to the caller.
    If entity is participant, removes it from its team. If entity is team, evacuates
    all participants from the team and makes them free agents.
    """
    if not get_confirmation(f"Delete the selected {get_model_type(entity)}?"):
        return USER_CANCEL

    if isinstance(entity, Participant):
        # remove participant its team
        team = entity.team()
        team.remove_participant(entity)

    if team.participants:
        # if team still has participants, make them free agents
        reassign_all_participants(team, destination_team)

    entity.delete()
