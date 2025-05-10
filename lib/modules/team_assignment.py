from models.participant import Participant
from models.team import Team
from util.nav_sentinels import PROCESS_CANCEL
from util.warnings import warn_team_full
from validation.enforcers import ensure_team_has_room


def main(
    participant: Participant,
    team: Team,
) -> None:
    """
    Checks to see if the provided team is under its membership cap
    and assigns the team's id to the participant's team_id attribute
    if there's room on the team. Warns the participant that the team
    is full and returns the cancellation sentinel OR returns the
    participant if there is room on the team.
    """
    if not team.is_free_agents:
        if not ensure_team_has_room(team):
            warn_team_full()
            return PROCESS_CANCEL

    new_participant = participant
    new_participant.team_id = team.id
    return new_participant
