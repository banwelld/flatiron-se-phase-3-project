from models.team.table_def import table_def
from util.validation.backend import validate_name
from util.database.helpers import (
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_all_rows,
    parse_db_row,
)


class Team:

    # cache of all teams

    all = {}

    # maximum number of players per team

    _MAX_CAPACITY = 5

    # instantiation assets

    def __init__(self, name: str, id: int = None):
        self.name = name
        self.id = id

    def __repr__(self):
        return f"{Team.__name__}: " f"name: {self.name}"

    def __str__(self):
        return f"{self.name}"

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
        TABLE_DEFs attribute with error handling in case table already
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
    def create(cls, name: str):
        """
        Instantiates a new team with only a name value and runs the
        save() method on the new instance and returns it, as well. As a
        precaution, builds the teamss table if none exists.
        """
        cls.build_table
        team = cls(name)
        team.save()
        return team

    @classmethod
    def fetch_all(cls):
        """
        Fetches all records from the 'teams' table. Returns a list
        of all Team instances or empty list if none found.
        """
        db_data = select_all_rows(table_def)
        return [parse_db_row(cls, row) for row in db_data]

    # instance methods

    def save(self):
        """
        Adds a new record to the teams table and assigns the row id to
        the new team's id property.
        """
        team_id = insert_row(table_def, name=self.name)
        self.id = team_id
        Team.all[self.id] = self
        return self

    def update(self):
        """
        Overwrites a team's database record with new values.
        """
        update_row(table_def, self.id, name=self.name)
        return self

    def delete(self):
        """
        Deletes team's database record, deletes the team's record in
        Team.all, and then nullifies self.id.
        """
        delete_row(table_def, self.id)
        del Team.all[self.id]
        self.id = None

    def participants(self):
        """
        Lists all the participants having the team's id as their team_id
        property.
        """
        from models.participant.cls import Participant

        print(self.id)
        return [
            mem for mem in Participant.all.values() if mem.team_id == self.id
        ] or Participant.fetch_all(self.id)
