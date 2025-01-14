from __init__ import CURSOR, CONN
from table_defs import TABLE_DEFS
from models.team import Team
from utility import (
    check_date_format,
    check_date_value,
    check_within_limits,
    check_characters,
    query_gen
)

"""
TODO: Change the error message for numbers in range
TODO: See why None appears instead of the actual value for poorly formatted date (ValueError: 'None' format invalid, expected 'YYYY/MM/DD')
TODO: Test: RecursionError: maximum recursion depth exceeded
            Team.fetch_by_id(4).members()
            Member.fetch_all()
            print(Member.fetch_by_name("Joe", "Blow"))
            Member.fetch_by_id(17).leave_current_team()
            Member.list_free_agents()
"""
class Member():
    
    all = {}
    
    table_def = "member_table"
    member_cap = 5
    
    def __init__(
        self, 
        first_name: str,
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None, 
        id: int | None = None
    ):

        # Validate birth_date format and month/day combination
        
        check_date_format(birth_date)
        check_date_value(birth_date)
        
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
        length = len(first_name)
        check_within_limits(length, 2, 20)
        check_characters(first_name, r"[^a-zA-Z '.\-]")
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        length = len(last_name)
        check_within_limits(length, 2, 30)
        check_characters(last_name, r"[^a-zA-Z '.\-]")
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
            if not Team.exists(team_id):
                raise ValueError(f"'{team_id}' not a valid team ID number.")
            if Team.fetch_by_id(team_id).isFull():
                raise OverflowError(
                    f"Team with ID '{team_id}' has reached its member limit.")           
        self._team_id = team_id
        
    def _attrib_names(self):
        return [key.lstrip("_") for key in vars(self).keys()].remove("id")
    
    def _attrib_vals(self):
        return [val for val in vars(self).values()].remove(self.id)
    
    @classmethod
    def create_table(cls):
        sql = query_gen("create", cls.table_def)
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        sql = query_gen("drop", cls.table_def)
        CURSOR.execute(sql)
        CONN.commit()
        
    def save(self):
        sql = query_gen(
            "insert",
            Member.table_def, 
            assignment_cols=self._attrib_names()
        )
        CURSOR.execute(sql, tuple(self._attrib_vals))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        sql = query_gen(
            "update", 
            Member.table_def,
            ["id"], 
            ["first_name", "last_name", "birth_date", "team_id"]
        )
        CURSOR.execute(
            sql, (
            self.first_name, 
            self.last_name, 
            self.birth_date, 
            self.team_id,
            self.id
        ))
        CONN.commit()
        
    @classmethod
    def create(
        cls,
        first_name: str, 
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None
    ):
        cls.create_table()
        member = Member(first_name, last_name, birth_date, team_id)
        member.save()
        return member
    
    def delete(self):
        sql = query_gen("delete", self.table_def)
        CURSOR.execute(sql, (self.id,),)
        CONN.commit()
                
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
    def fetch_all(cls):
        sql = query_gen("select", cls.table_def)
        data = CURSOR.execute(sql).fetchall()
        return [cls.parse_db_row(row) for row in data]
    
    def fetch_by_criteria(cls, col_name: str, criteria: str | int):
        sql = query_gen("select", cls.table_def, [col_name])
        db_row = CURSOR.execute(sql, (criteria,)).fetchone()
        
        if db_row:
            return cls.parse_db_row(db_row)
        return None

    def leave_current_team(self):
        """Assigns team_id attribute of None to the member instance. If
        the team instance to which the member instance was assigned has
        a captain_id attribute equal to the member inetance's id,
        invokes the vacate_captain() method on the team instance.
        Updates the database record after all changes made.
        
        Raises Exception if the member instance has team_id attribute
        equal to None.
        """
        if not self.team_id:
            raise Exception(
                f"Member '{self.id}' has no team_id value")
            
        my_team = Team.fetch_by_criteria("team_id", self.team_id)
        
        if self.id == my_team.captain_id:
            my_team.vacate_captain()
            
        self.team_id = None
        self.update()

    def join_team(self, team_id: int):
        """Assigns the specified team_id attribute value to the member
        instance. If the member instance already has a valid team_id
        attribute, invokes the leave_current_team() method before
        assigning the specified team_id to the member instance.
        
        Raises ValueError for invalid team_id or Exception if member is
        already assigned to the specified team.
        """
        if self.team_id is not None:
            if not Team.exists(team_id):
                raise ValueError(f"'{team_id}' invalid team_id")
            
            if self.team_id == team_id:
                raise Exception(
                    f"Member '{self.id}' is already associated with team '{team_id}'")
            
            self.leave_current_team()
        
        self.team_id = team_id
        self.update()
            
    @classmethod
    def list_free_agents(cls):
        return [
            member for member in cls.fetch_all()
            if member.team_id == None]