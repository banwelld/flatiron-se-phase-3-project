import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    PARTICIPANT_MODEL_CONFIG as MODEL_CONFIG,
    PARTICIPANT_TABLE_CONFIG as TABLE_CONFIG,
)
from validation.backend import validate_name, validate_date
from util.db_helpers import (
    create_table,
    drop_table,
    insert_row,
    update_row,
    del_row,
    select_all_rows,
    parse_db_row,
)


class Participant:
    CONFIG = MODEL_CONFIG

    def __init__(
        self,
        f_name: str,
        l_name: str,
        birth_date: str,
        team_id: int = None,
        id: int = None,
    ):
        self.f_name = f_name
        self.l_name = l_name
        self.birth_date = birth_date
        self.team_id = team_id
        self.id = id

    def __repr__(self):
        return f"<<PARTICIPANT: {self.l_name.upper()}, {self.f_name} (id {self.id}, team {self.team_id})>>"

    @property
    def f_name(self):
        return self._f_name

    @f_name.setter
    @validate_name("participant", "f_name")
    def f_name(self, f_name):
        self._f_name = f_name

    @property
    def l_name(self):
        return self._l_name

    @l_name.setter
    @validate_name("participant", "l_name")
    def l_name(self, l_name):
        self._l_name = l_name

    @property
    def birth_date(self):
        return self._birth_date

    @birth_date.setter
    @validate_date("participant", "birth_date")
    def birth_date(self, birth_date):
        self._birth_date = birth_date

    @classmethod
    def build_table(cls):
        """
        Creates a table based on the table schema in the class's
        table_defs attribute with error handling in case table already
        exists.
        """
        create_table(TABLE_CONFIG)

    @classmethod
    def del_table(cls):
        """
        Deletes the table associated to the current class in its
        _TABLE_DEF attribute.
        """
        drop_table(TABLE_CONFIG)

    @classmethod
    def create(cls, f_name: str, l_name: str, birth_date: str):
        """
        Instantiates a new participant with f_name, l_name, and
        birth_date values and runs the save() method on the new instance
        and returns it. As a precaution, builds the participants table if
        none exists.
        """
        cls.build_table()
        return Participant(f_name, l_name, birth_date)

    @classmethod
    def fetch(cls, team_id: int = None):
        """
        Fetches all records from the 'participants' table. Returns a list
        of all Participant instances or empty list if none found. 'team_id'
        value is persisted to the database as the SST for membership on the
        back end. Front end membership is managed by the teams.
        """
        db_data = select_all_rows(TABLE_CONFIG, team_id)
        return [parse_db_row(cls, row) for row in db_data]

    def save(self):
        """
        Adds a new participant's record to the participants table and assigns the
        row id to the participant's id property. When appended to a team's
        participants list, the participant data will be updated to the database
        with the team's ID.
        """
        participant_id = insert_row(
            TABLE_CONFIG,
            f_name=self.f_name,
            l_name=self.l_name,
            birth_date=self.birth_date,
            team_id=self.team_id,
        )
        self.id = participant_id

    def update(self):
        """
        Overwrites a participant's database record with info changes. Allows
        for the team_id to be passed in and sent to the database, enabling a
        foreign-key relationship between members and teams in the database,
        while relating through object-orientation in the code.
        """
        updates = {
            "f_name": self.f_name,
            "l_name": self.l_name,
            "birth_date": self.birth_date,
            "team_id": self.team_id,
        }
        update_row(
            TABLE_CONFIG,
            self.id,
            **updates,
        )
        return self

    def delete(self):
        """
        Deletes participant's database record, removes the participant's record
        in its team's participants list, and then nullifies self.id.
        """
        del_row(TABLE_CONFIG, self.id)
        self.id = None

    def team(self):
        """
        Returns the team associated with the participant.
        """
        from models.team import Team

        my_team = Team.fetch(self.team_id)
        return next(my_team, None)
