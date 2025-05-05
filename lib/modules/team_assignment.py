from models.participant import Participant
from models.team import Team
from modules.get_confirmation import get_confirmation
from util.user_sentinels import USER_CANCEL, PROCESS_CANCEL
from util.warnings import warn_team_full
from util.helpers import generate_disp_text
from validation.enforcers import ensure_team_has_room


# utility function


def reassign_all_participants(source_team: Team, destination_team: Team) -> None:
    """
    Makes a copy of the source team's participants list and iterates over that
    to remove participants from the source team and append them to the destination
    team. Suppresses user confirmation for the operation.
    """
    for p in list(source_team.participants):
        main(p, destination_team, source_team, do_confirm=False)


# control flow


def main(
    participant: Participant,
    destination_team: Team,
    source_team: Team = None,
    do_confirm: bool = True,
) -> None:
    """
    Handles the assignment of a participant to a team. Throws a warning and returns early if team
    is full. Confirms user's intent, returning sentinel if the user chooses to cancel. If the
    participant is moving from another team, it removes them from that team. The
    append_participant method persists the change to the database.
    """
    if not destination_team.is_free_agents:
        if not ensure_team_has_room(destination_team):
            warn_team_full()
            return PROCESS_CANCEL

    if do_confirm:
        confirmation_prompt = (
            f"Move {generate_disp_text(participant)} "
            f"to {generate_disp_text(destination_team)}?"
        )
        if not get_confirmation(confirmation_prompt):
            return USER_CANCEL

    if source_team:
        source_team.remove_participant(participant)
    destination_team.append_participant(participant, do_persist=True)
