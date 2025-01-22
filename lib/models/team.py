from program_settings import PROGRAM_SETTINGS as PS
from utility import (
    enforce_range,
    validate_chars,
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_rows,
    select_by_id
)

class Team():

    all = {}
    
    # hold a single team in state
    
    _current = None
    
    # table definition attribute
    
    _table_def = PS["Team"]["table_def"]
    
    # instantiation assets
        
    def __init__(
        self,
        name: str,
        captain_id: int | None = None,
        id: int | None = None
    ):
        self.name = name
        self.captain_id = captain_id
        self.id = id

    def __repr__(self):
        from models.member import Member
        if captain := Member.fetch_by_id(self.captain_id):
            captain_name = f"'{captain.first_name} {captain.last_name}'"
        else:
            captain_name = "*VACANT*"
            
        return (
            f"<{type(self).__name__.upper()}: "
            f"name = '{self.name}', "
            f"captain = {captain_name}>"
        )
                
    def __str__(self):
        return f"{self.name}"
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        length = len(name)
        enforce_range(length, 4, 30)
        validate_chars(name, r"[^a-zA-Z0-9 '.\-]")
        self._name = name
    
    @property
    def captain_id(self):
        return self._captain_id
    
    @captain_id.setter
    def captain_id(self, captain_id):
        from models.member import Member
        if (isinstance(captain_id, int) and 
            Member.fetch_by_id(captain_id)) or captain_id is None:
            self._captain_id = captain_id
        else:
            raise ValueError("Invalid captain_id value. Expected an integer "
                             "referencing a row in the teams table.")
    
    @classmethod
    def build_table(cls):
        """
        Creates a table based on the table schema in the class's
        table_defs attribute.
        """
        create_table(cls._table_def)
        
    @classmethod
    def delete_table(cls):
        """
        Deletes the table associated to the current class in its
        table_def attribute.
        """
        drop_table(cls._table_def)
        
    def save(self):
        """
        Adds a new team's record to the teams table and assigns the
        row id to the team's id property.
        """
        team_id = insert_row(
            Team._table_def,
            name=self.name,
            captain_id=self.captain_id
        )
        self.id = team_id
        type(self).all[self.id] = self
    
    def update(self):
        """Overwrites a team's database record with new values."""
        update_row(
            Team._table_def,
            self.id,
            name=self.name,
            captain_id=self.captain_id
        )
        
    @classmethod
    def create(cls, name: str):
        """
        Instantiates a new team with only a name value. Runs the save()
        method on the new instance and returns it, as well. As a
        precaution, builds the teamss table if none exists.
        """
        cls.build_table
        team = cls(name)
        team.save()
        return team
    
    def delete(self):
        """
        Deletes team's database record, then deletes the team's record in
        Team.all and nullifies self.id.
        """
        delete_row(Team._table_def, self.id)
        del Team.all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """
        Using a team record from the teams table, checks if an
        instance for the team exists in Team.all and, if so, 
        overwrites the existing instance's properties. If no instance in
        Team.all matches the the database record, then instantiates
        new instance from the record's data and adds it to Team.all.
        Returns the team instance.
        """
        if team := cls.all.get(record[0]):
            team.name = record[1]
            team.captain_id = record[2]
            
        else:
            team = cls(record[1], record[2])
            team.id = record[0]
            cls.all[team.id] = team
            
        return team
    
    @classmethod
    def fetch_all(cls, **params):
        """
        Fetches all matching records from the 'teams' table, filtered
        based the 'params' keyword arguments, if any. Returns a list of
        all matching team instances or empty list if none found.
        """
        db_data = select_rows(cls._table_def, **params)
        teams = [cls.parse_db_row(row) for row in db_data]
        return teams
    
    @classmethod
    def fetch_by_id(cls, id: int):
        """
        Returns the team instance of the team whose primary key value
        matches the id argument. Returns None if no match.
        """
        if db_data := select_by_id(cls._table_def, id):
            return cls.parse_db_row(db_data)
        return None
    
    @classmethod
    def set_current(cls, member=None):
        """Sets a member instance to _current to hold it in state"""
        cls._current = member
        return cls._current
    
    @classmethod
    def get_current(cls):
        """Returns the current value of _current"""
        return cls._current