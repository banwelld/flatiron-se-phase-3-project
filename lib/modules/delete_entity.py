import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from modules.get_confirmation import get_confirmation
from modules.team_assignment import reassign_all_participants
from modules.user_sentinels import USER_CANCEL
from util.helpers import get_model_type, generate_disp_text


# operational control flow


def delete_entity(entity: Union[Participant, Team], destination_team: Team = None):
    """
    Confirms user's intent and deletes the selected entity of the specified model
    type with confirmation. If user cancels, sends the back sentinel to the caller.
    If entity is participant, removes it from its team. If entity is team, evacuates
    all participants from the team and makes them free agents.
    """
    entity_name = generate_disp_text(entity)

    if not get_confirmation(
        f"Delete selected {get_model_type(entity)}: {entity_name}?"
    ):
        from cli import selected_entities

        selected_entities.reset()
        return USER_CANCEL

    if isinstance(entity, Participant):
        # remove participant from its team
        team = entity.team()
        team.remove_participant(entity)

    if isinstance(entity, Team):
        if entity.participants:
            # if team still has participants, make them free agents
            reassign_all_participants(entity, destination_team)

    entity.delete()
