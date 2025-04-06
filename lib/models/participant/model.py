from models.participant.table_def import table_def
from util.validation.backend import validate_name, validate_date
from util.database.helpers import (
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_all_rows,
    parse_db_row,
)


class Participant:

    # cache of all participants

    all = {}

    # instantiation assets

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: str,
        team_id: int = None,
        id: int = None,
    ):

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.team_id = team_id
        self.id = id

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    @validate_name("participant", "first_name")
    def first_name(self, first_name):
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    @validate_name("participant", "last_name")
    def last_name(self, last_name):
        self._last_name = last_name

    @property
    def birth_date(self):
        return self._birth_date

    @birth_date.setter
    @validate_date("participant", "birth_date")
    def birth_date(self, birth_date):
        self._birth_date = birth_date

    # class methods

    @classmethod
    def build_table(cls):
        """
        Creates a table based on the table schema in the class's
        table_defs attribute with error handling in case table already
        exists.
        """
        create_table(table_def)

    @classmethod
    def delete_table(cls):
        """
        Deletes the table associated to the current class in its
        _TABLE_DEF attribute.
        """
        drop_table(table_def)

    @classmethod
    def create(cls, first_name: str, last_name: str, birth_date: str):
        """
        Instantiates a new participant with first_name, last_name, and
        birth_date values and runs the save() method on the new instance
        and returns it. As a precaution, builds the participants table if
        none exists.
        """
        cls.build_table()
        participant = Participant(first_name, last_name, birth_date)
        participant.save()
        return participant

    @classmethod
    def fetch_all(cls, team_id: int = None):
        """
        Fetches all records from the 'participants' table. Returns a list
        of all Participant instances or empty list if none found.
        """
        db_data = select_all_rows(table_def, team_id)
        return [parse_db_row(cls, row) for row in db_data]

    # instance methods

    def save(self):
        """
        Adds a new participant's record to the participants table and assigns the
        row id to the participant's id property.
        """
        participant_id = insert_row(
            table_def,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id,
        )
        self.id = participant_id
        Participant.all[self.id] = self

    def update(self):
        """
        Overwrites a participant's database record with new values.
        """
        update_row(
            table_def,
            self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id,
        )
        return self

    def delete(self):
        """
        Deletes participant's database record, delete's the participant's record
        in Participant.all, and then nullifies self.id.
        """
        delete_row(table_def, self.id)
        del Participant.all[self.id]
        self.id = None

    def team(self):
        """
        Returns the team name associated with the participant.
        """
        from models.team.model import Team

        if self.team_id is None:
            return None
        return Team.all[self.team_id].name
