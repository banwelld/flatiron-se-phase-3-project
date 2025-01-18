from __init__ import CURSOR, CONN
from program_settings import PROGRAM_SETTINGS as PS
from utility import (
    check_date_format as form_check,
    check_date_value as val_check,
    check_within_limits as lim_check,
    check_characters as char_check,
    create_table,
    drop_table,
    write_data,
    delete_row,
    select_rows
)

class Member():
    
    all = {}
    
    _table_def = PS["Member"]["table_def"]
    
    def __init__(
        self, 
        first_name: str,
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None, 
        id: int | None = None
    ):

        # Validate birth_date format and month/day combination
        
        form_check(birth_date)
        val_check(birth_date)
        
        self.first_name = first_name
        self.last_name = last_name
        self._birth_date = birth_date
        self.team_id = team_id
        self.id = id
        
    def __str__(self):
        return f"{type(self).__name__.upper()}: {self.first_name} {self.last_name}"
        
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, first_name):
        lim_check(len(first_name), 2, 20)
        char_check(first_name, r"[^a-zA-Z '.\-]")
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        lim_check(len(last_name), 2, 30)
        char_check(last_name, r"[^a-zA-Z '.\-]")
        self._last_name = last_name
        
    @property
    def birth_date(self):
        return self._birth_date
    
    @property
    def team_id(self):
        return self._team_id
    
    @team_id.setter
    def team_id(self, team_id):
        if team_id is not None:                
            member_count = len(Member.fetch_rows(team_id=team_id))
            if member_count >= PS["Team"]["member_limit"]:
                raise OverflowError(
                    "Team is at capacity. Cannot accept new members")
        self._team_id = team_id
    
    @classmethod
    def build_table(cls):
        create_table(cls._table_def)
        
    @classmethod
    def delete_table(cls):
        drop_table(cls._table_def)
        
    def save(self):
        new_member_id = write_data(
            Member._table_def, 
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id
        )
        
        self.id = new_member_id
        type(self).all[self.id] = self
    
    def update(self):
        write_data(
            Member._table_def,
            self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            team_id=self.team_id
        )
        
    @classmethod
    def create(cls, first_name: str, last_name: str, birth_date: str):
        cls.build_table()
        member = Member(first_name, last_name, birth_date)
        member.save()
        return member
    
    def delete(self):
        delete_row(Member._table_def, self.id)
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """Reconstitute a member instance from the member's database record.
        """
        if member := cls.all.get(record[0]):
            member.first_name = record[1]
            member.last_name = record[2]
            member._birth_date = record[3]
            member.team_id = record[4]
        else:
            member = Member(record[1], record[2], record[3], record[4])
            member.id = record[0]
            cls.all[member.id] = member
        return member
    
    @classmethod
    def fetch_rows(cls, **params):
        """
        Fetches all matching records from the 'members' table, filtered
        based on 'params' keyword arguments, if any. Returns a list of
        all matching member instances or empty list if none found.
        """

        db_data = select_rows(cls._table_def, **params)
        members = [cls.parse_db_row(row) for row in db_data]
        return members

    def leave_current_team(self):
        """
        Assigns team_id attribute of None to the member instance. If the
        team instance to which the member instance was assigned has a
        captain_id attribute equal to the member inetance's id, invokes
        the dump_captain() method on the team instance. Updates the
        database record after all changes made.
        
        Raises ValueError if the member instance has team_id attribute
        equal to None.
        """
        from models.team import Team
        
        if self.team_id is None:
            raise ValueError(
                f"Member '{self.id}' has no team_id value")
            
        my_team = Team.fetch_rows(id=self.team_id).pop()
        if my_team.captain_id == self.id:
            my_team.dump_captain()
            
        self.team_id = None
        self.update()

    def join_team(self, team_id: int):
        """Assigns the specified team_id attribute value to the member
        instance.
        
        Raises ValueError if the member already belongs to the team or
        PermissionError if the member belongs to another team already.
        """
        if self.team_id is not None:
            
            if self.team_id == team_id:
                raise ValueError(
                    "Member already assigned to the designated team.")
            
            raise PermissionError(
                "Members cannot belong to more than one team.")
            
        self.team_id = team_id
        self.update()
            
    @classmethod
    def free_agents(cls):
        return cls.fetch_rows(team_id=None)