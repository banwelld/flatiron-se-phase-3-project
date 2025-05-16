import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
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
    CONFIG = MODEL_CONFIG

    def __init__(self, name: str, is_free_agents: bool = False):
        self.name = name
        self.is_free_agents = is_free_agents
        self.id = None

    def __repr__(self):
        return f"<<TEAM: {self.name}>>"

    @property
    def name(self):
        return self._name

    @name.setter
    @validate_name("team", "name")
    def name(self, name):
        self._name = name

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
        return team

    @classmethod
    def fetch(cls, tid: int = None):
        """
        Fetches all records from the 'teams' table. Returns a list
        of all Team instances or empty list if none found.
        """
        db_data = select_all_rows(TABLE_CONFIG, tid)
        result = [parse_db_row(cls, row) for row in db_data]
        return result

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
        Deletes team's database record and then nullifies self.id.
        """
        delete_row(TABLE_CONFIG, self.id)
        self.id = None

    def fetch_participants(self) -> list:
        """
        Uses the Participant.fetch() method to load all participants tagged
        with self.id.
        """
        from models.participant import Participant

        return Participant.fetch(self.id)
