from program_settings import PROGRAM_SETTINGS as PS
from utility import (
    enforce_range,
    validate_chars,
    enforce_valid_date,
    create_table,
    drop_table,
    insert_row,
    update_row,
    delete_row,
    select_all_rows,
    select_one_row,
    enforce_int_type,
)

class Member():
    
    all = {}
    
    # single member held in state
    
    _current = None
    
    # table definition attribute
    
    _table_def = PS['Member']['table_def']
    
    # attribute disp_namelay names
    
    attrib_details = {
        "id": {
            "attrib_name": "id",
            "disp_name": "ID",
            "info_type": "mem_id",
            "data_type": "integer",
            "operations": ["id_search"],
            },
        "first_name":{
            "attrib_name": "first_name",
            "disp_name": "first name",
            "info_type": "name",
            "data_type": "string",
            "min_length": 2,
            "max_length": 20,
            "char_regex": r"[^a-zA-Z '.\-]",
            "operations": ["new", "name_search", "update"],
        },
        "last_name": {
            "disp_name": "last name",
            "attrib_name": "last_name",
            "info_type": "name",
            "data_type": "string",
            "min_length": 2,
            "max_length": 30,
            "char_regex": r"[^a-zA-Z '.\-]",
            "operations": ["new", "name_search", "update"],
        },
        "birth_date": {
            "attrib_name": "birth_date",
            "disp_name": "birth date",
            "info_type": "date",
            "data_type": "string",
            "min_length": 10,
            "max_length": 10,
            "date_regex": r"^[0-9]{4}(/[0-9]{2}){2}$",
            "operations": ["new", "update"],
        },
        "team_id": {
            "attrib_name": "team_id",
            "disp_name": "ID",
            "info_type": "team_id",
            "data_type": "integer",
            "operations": ["update"],
        },
    }
    
    # instantiation assets
    
    def __init__(
        self, 
        first_name: str,
        last_name: str, 
        birth_date: str, 
        team_id: int = None,
        id: int = None
    ):
        
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.team_id = team_id
        self.id = id
        
    def __repr__(self):
        return (
            f"<{type(self).__name__.upper()}: "
            f"first_name = '{self.first_name}', "
            f"last_name = '{self.last_name}', "
            f"team = {self.team_name()}>"
        )
                
    def __str__(self):
        from ui_rendering import list_str
        member = list_str(f"{self._name()} : {self.birth_date} : "
                          f"{self.team_name()}")
        return member
    
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, first_name):
        enforce_range(
            len(first_name),
            Member.attrib_details['first_name']['min_length'],
            Member.attrib_details['first_name']['max_length'],
        )
        validate_chars(
            first_name,
            Member.attrib_details['first_name']['char_regex']
        )
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        enforce_range(
            len(last_name),
            Member.attrib_details['last_name']['min_length'],
            Member.attrib_details['last_name']['max_length']
        )
        validate_chars(
            last_name,
            Member.attrib_details['last_name']['char_regex']
        )
        self._last_name = last_name
        
    @property
    def birth_date(self):
        return self._birth_date
    
    @birth_date.setter
    def birth_date(self, birth_date):
        enforce_valid_date(
            birth_date,
            Member.attrib_details['birth_date']['date_regex']
        )
        self._birth_date = birth_date
    
    @property
    def team_id(self):
        return self._team_id
    
    @team_id.setter
    def team_id(self, team_id):
        if team_id is not None:
            enforce_int_type(team_id)
        self._team_id = team_id
        
    # methods
    
    def _name(self):
        return f"{self.first_name} {self.last_name}"
    
    def team_name(self):
        from ui_rendering import warning_str, list_str
        from models.team import Team
        team = next(
            (t for t in Team.fetch_all() if t.id == self.team_id),
            None
        )
        return list_str(team.name) if team else warning_str("* FREE AGENT *")

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
        Member.all[self.id] = self
    
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
        return self
        
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
                record[1], record[2],
                record[3], record[4]
            )
            member.id = record[0]
            cls.all[member.id] = member
            
        return member
    
    @classmethod
    def fetch_all(cls):
        """
        Fetches all matching records from the 'members' table, filtered
        based on 'params' keyword arguments, if any. Returns a list of
        all matching member instances or empty list if none found.
        """
        db_data = select_all_rows(cls._table_def)
        return [cls.parse_db_row(row) for row in db_data]
    
    @classmethod
    def fetch_by_id(cls, id: int):
        """
        Returns the member instance of the member whose primary key
        value matches the id argument. Returns None if no match.
        """
        if db_data := select_one_row(cls._table_def, id=id):
            return cls.parse_db_row(db_data)
        return None
    
    @classmethod
    def fetch_by_name(cls, first_name: str, last_name: str):
        """
        Returns the member instance of the member whose primary key
        value matches the id argument. Returns None if no match.
        """
        if db_data := select_one_row(
                cls._table_def,
                first=first_name,
                last=last_name
        ):
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