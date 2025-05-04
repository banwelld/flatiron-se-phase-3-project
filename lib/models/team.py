import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.get_config import (
    TEAM_MODEL_CONFIG as MODEL_CONFIG,
    TEAM_TABLE_CONFIG as TABLE_CONFIG,
)
from validation.backend import validate_name
from util.db_helpers import (
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_all_rows,
    parse_db_row,
)


class Team:
    #  configuration

    CONFIG = MODEL_CONFIG

    # cache of all teams

    all = []

    # constructor

    def __init__(
        self,
        name: str,
        is_free_agents: bool = False,
    ):
        self.name = name
        self.is_free_agents = is_free_agents
        self.participants = []
        self.id = None

    def __repr__(self):
        return self.name

    # properties

    @property
    def name(self):
        return self._name

    @name.setter
    @validate_name("team", "name")
    def name(self, name):
        self._name = name

    # class methods

    @classmethod
    def build_table(cls):
        """
        Creates a table based on the table schema in the class's
        TABLE_CONFIG with error handling in case table already
        exists.
        """
        create_table(TABLE_CONFIG)

    @classmethod
    def delete_table(cls):
        """
        Deletes the table associated to the current class.
        """
        drop_table(TABLE_CONFIG)

    @classmethod
    def create(cls, name: str, is_free_agents: bool = False):
        """
        Instantiates a new team with only a name value and runs the
        save() method on the new instance and returns it, as well. As a
        precaution, builds the teamss table if none exists.
        """
        cls.build_table
        team = cls(name, is_free_agents)
        team.save()
        return team

    @classmethod
    def fetch_all(cls):
        """
        Fetches all records from the 'teams' table. Returns a list
        of all Team instances or empty list if none found.
        """
        db_data = select_all_rows(TABLE_CONFIG)
        result = [parse_db_row(cls, row) for row in db_data]
        return result

    # instance methods

    def save(self):
        """
        Adds a new record to the teams table and assigns the row id to
        the new team's id property.
        """
        team_id = insert_row(
            TABLE_CONFIG,
            name=self.name,
            is_free_agents=self.is_free_agents,
        )
        self.id = team_id
        Team.all.append(self)
        return self

    def update(self):
        """
        Overwrites a team's database record with new values.
        """
        update_row(
            TABLE_CONFIG,
            self.id,
            name=self.name,
            is_free_agents=self.is_free_agents,
        )
        return self

    def delete(self):
        """
        Deletes team's database record, removes the team from Team.all,
        and then nullifies self.id.
        """
        delete_row(TABLE_CONFIG, self.id)
        Team.all.remove(self)
        self.id = None

    def fetch_participants(self):
        """
        Uses the Participant.fetch_all() method to load all participants tagged
        with self.id. No team capacity check so that full team loads even if default
        capacity changes. Managers shall remove partitipants from team manually to
        remain in compliance.
        """
        from models.participant import Participant

        Participant.fetch_all(self.id)

    def append_participant(self, participant, do_persist: bool = False):
        """
        Adds a participant to the team and persists the assignment if do_persist has
        a value of True. The Participant.update() method allows for the team_id to be
        passed to it, enabling a foreign-key relationship between members and teams in
        the database, while relating through object-orientation in the code.
        """
        self.participants.append(participant)
        if do_persist:
            participant.update(self.id)

    def remove_participant(self, participant):
        """
        Removes a participant from the team. Does NOT persist the removal as this will be
        performed when adding to a new team, including the free agent team.
        """
        self.participants.remove(participant)
