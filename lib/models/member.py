from program_settings import PROGRAM_SETTINGS as PS
from models.team import Team
from utility import (
    enforce_range,
    validate_chars,
    validate_date,
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_rows,
    select_by_id
)

class Member():
    
    all = {}
    
    # table definition attribute
    
    _table_def = PS["Member"]["table_def"]
    
    # instantiation assets
    
    def __init__(
        self, 
        first_name: str,
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None,
        id: int | None = None
    ):
        
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.team_id = team_id
        self.id = id

    def __repr__(self):
        team_name = (
            f"'{Team.fetch_by_id(self.team_id)}'" if self.team_id 
            else "*FREE AGENT*"
        )
        return (
            f"<{type(self).__name__.upper()}: "
            f"first_name = '{self.first_name}', "
            f"last_name = '{self.last_name}', "
            f"team = {team_name}>"
        )
                
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, first_name):
        enforce_range(len(first_name), 2, 20)
        validate_chars(first_name, r"[^a-zA-Z '.\-]")
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        enforce_range(len(last_name), 2, 30)
        validate_chars(last_name, r"[^a-zA-Z '.\-]")
        self._last_name = last_name
        
    @property
    def birth_date(self):
        return self._birth_date
    
    @birth_date.setter
    def birth_date(self, birth_date):
        validate_date(birth_date)
        self._birth_date = birth_date
    
    @property
    def team_id(self):
        return self._team_id
    
    @team_id.setter
    def team_id(self, team_id):
        if (isinstance(team_id, int) and 
            Team.fetch_by_id(team_id)) or team_id is None:
            self._team_id = team_id
        else:
            raise ValueError("Invalid team_id value. Expected an integer "
                             "referencing a row in the teams table.")
        
    # methods
    
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
        Adds a new member's record to the members table and assigns the
        row id to the member's id property.
        """
        member_id = insert_row(
            Member._table_def, 
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id
        )
        self.id = member_id
        type(self).all[self.id] = self
    
    def update(self):
        """Overwrites a member's database record with new values."""
        update_row(
            Member._table_def,
            self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id
        )
        
    @classmethod
    def create(cls, first_name: str, last_name: str, birth_date: str):
        """
        Instantiates a new member with first_name, last_name, and
        birty_day values, which are mandatory. Runs the save() method
        on the new instance and returns it, as well. As a precaution,
        builds the members table if none exists.
        """
        cls.build_table()
        member = Member(first_name, last_name, birth_date)
        member.save()
        return member
    
    def delete(self):
        """
        Deletes member's record in in the members table and in Member.all and
        then nullifies self.id.
        """            
        delete_row(Member._table_def, self.id)
        del Member.all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """
        Using a member record from the members table, checks if an
        instance for the member exists in Member.all and, if so, 
        overwrites the existing instance's properties. If no instance in
        Member.all matches the the database record, then instantiates
        new instance from the record's data and adds it to Member.all.
        Returns the member instance. Imports the Team class in order to
        assign the member's team to its team property.
        """        
        if member := cls.all.get(record[0]):
            member.first_name = record[1]
            member.last_name = record[2]
            member.birth_date = record[3]
            member.team_id = record[4]
            
        else:
            member = Member(
                record[1],
                record[2],
                record[3],
                record[4]
            )
            member.id = record[0]
            cls.all[member.id] = member
            
        return member
    
    @classmethod
    def fetch_all(cls, **params):
        """
        Fetches all matching records from the 'members' table, filtered
        based on 'params' keyword arguments, if any. Returns a list of
        all matching member instances or empty list if none found.
        """
        db_data = select_rows(cls._table_def, **params)
        members = [cls.parse_db_row(row) for row in db_data]
        return members
    
    @classmethod
    def fetch_by_id(cls, id: int):
        """
        Returns the member instance of the member whose primary key
        value matches the id argument. Returns None if no match.
        """
        if db_data := select_by_id(cls._table_def, id):
            return cls.parse_db_row(db_data)
        return None