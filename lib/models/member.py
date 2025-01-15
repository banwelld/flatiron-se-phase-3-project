from __init__ import CURSOR, CONN
from lib.program_settings import PROGRAM_SETTINGS as PS
from models.team import Team
from utility import (
    check_date_format,
    check_date_value,
    check_within_limits,
    check_characters,
    query_gen
)

"""
TODO: Recursion Error when testing list_free_agents()

"""
class Member():
    
    all = {}
    
    _table_def = PROGRAM_SETTINGS["Member"]["table_def"]
    
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
        check_within_limits(len(first_name), 2, 20)
        check_characters(first_name, r"[^a-zA-Z '.\-]")
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        check_within_limits(len(last_name), 2, 30)
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
        if (hasattr(self, "id") and
            team_id is not None and
            self.team_id is not None
        ):
            raise PermissionError(
                f"Cannot overwrite team assignment. Please vacate member's "
                "current team_id before assigning a new one."
            )
        team_size = len(Member.fetch_by_criteria("team_id", team_id))
        if team_size >= PS["Team"]["member_limit"]:
            raise OverflowError("Team is at capacity.")
       
        self._team_id = team_id
    
    @classmethod
    def create_table(cls):
        sql = query_gen("create", cls._table_def)
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        sql = query_gen("drop", cls._table_def)
        CURSOR.execute(sql)
        CONN.commit()
        
    def save(self):
        sql = query_gen(
            "insert",
            Member._table_def, 
            assignment_cols=[
                "first_name", "last_name", "birth_date", "team_id"]
        )
        CURSOR.execute(sql, (
            self.first_name, 
            self.last_name, 
            self.birth_date, 
            self.team_id
        ))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        sql = query_gen(
            "update", 
            Member._table_def,
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
        sql = query_gen("delete", Member._table_def, ["id"])
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
        sql = query_gen("select", cls._table_def)
        db_rows = CURSOR.execute(sql).fetchall()
        return [cls.parse_db_row(row) for row in db_rows]
    
    @classmethod
    def fetch_by_criteria(cls, col_name: str, criteria: str | int):
        sql = query_gen("select", cls._table_def, [col_name])
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
            raise ValueError(
                f"Member '{self.id}' has no team_id value")
            
        my_team = Team.fetch_by_criteria("id", self.team_id)
        
        if self.id == my_team.captain_id:
            my_team.vacate_captain()
            
        self.team_id = None
        self.update()

    def join_team(self, team_id: int):
        """Assigns the specified team_id attribute value to the member
        instance.
        """
        self.team_id = team_id
        self.update()
            
    @classmethod
    def free_agents(cls):
        return [
            member for member in cls.fetch_all()
            if member.team_id == None]