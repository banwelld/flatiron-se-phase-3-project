from models.participant import Participant
from models.team import Team
from modules.get_confirmation import get_confirmation
from modules.user_sentinels import USER_CANCEL
from modules.warnings import warn_team_full
from util.helpers import generate_disp_name
from validation.enforcers import ensure_team_not_full
from strings.user_messages import YN_PROMPT


# team assignment functions

def assign_to_team(
    participant: Participant,
    destination_team: Team,
    source_team: Team = None,
    do_confirm: bool = True,
) -> None:
    """
    Handles the assignment of a participant to a team. Confirms user's intent, returning sentinel
    if the user chooses to cancel. If the participant is moving from another team, it removes them
    from that team. The append_participant method persists the change to the database.
    """
    if do_confirm:
        confirmation_prompt = (
            f"Move {generate_disp_name(participant)} "
            f"to {generate_disp_name(destination_team)}?"
        )
        if not get_confirmation(confirmation_prompt):
            return USER_CANCEL
        
    if not destination_team.is_free_agents:
        if ensure_team_not_full(destination_team) is False:
            return warn_team_full()

    if source_team:
        source_team.remove_participant(participant)
    destination_team.append_participant(participant, do_persist=True)


def reassign_all_participants(source_team: Team, destination_team: Team) -> None:
    """
    Makes a copy of the source team's participants list and iterates over that
    to remove participants from the source team and append them to the destination
    team. Suppresses user confirmation for the operation.
    """
    for p in list(source_team.participants):
        assign_to_team(p, destination_team, source_team, do_confirm=False)
