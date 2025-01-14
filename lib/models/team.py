from __init__ import CURSOR, CONN
from utility import (
    check_within_limits,
    check_characters,
    query_gen    
)

# TODO: Consider refactoring of captain_id.setter

class Team():
    
    all = {}
    
    table_def = "team_table"
    member_cap = 5
        
    def __init__(
        self,
        name: str,
        captain_id: int | None = None,
        id: int | None = None
    ):
        self.name = name
        self.captain_id = captain_id
        self.id = id
                
    def __str__(self):
        return f"{type(self).__name__.upper()}: {self.name}"
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        length = len(name)
        check_within_limits(length, 4, 30)
        check_characters(name, r"[^a-zA-Z '.\-]")
        self._name = name
    
    @property
    def captain_id(self):
        return self._captain_id
    
    @captain_id.setter
    def captain_id(self, captain_id):
        if (hasattr(self, "id") and 
            self.id is not None and 
            captain_id is not None
        ):
            members = [member.id for member in self.members()]
            if captain_id not in members:
                raise ValueError(
                    f"ID '{captain_id}' does not belong to a current team "
                    "member"
                )
        self._captain_id = captain_id
    
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
            Team.table_def, 
            assignment_cols=["name", "captain_id"]
        )
        CURSOR.execute(sql, (self.name, self.captain_id))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        sql = query_gen(
            "update", 
            Team.table_def, 
            ["id"], 
            ["name", "captain_id"]
        )
        CURSOR.execute(sql, (self.name, self.captain_id, self.id))
        CONN.commit()
        
    @classmethod
    def create(cls, name: str):
        team = cls(name)
        team.save()
        return team
    
    def delete(self):
        sql = query_gen("delete", Team.table_def, ["id"])
        CURSOR.execute(sql, (self.id,),)
        CONN.commit()
        
        for member in self.members():
            self.remove_member(member.id)
                
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """Reconstitute a team instance from the team's record in the
        teams table.
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
    def fetch_all(cls):
        sql = query_gen("select", cls.table_def)
        db_rows = CURSOR.execute(sql).fetchall()
        return [cls.parse_db_row(row) for row in db_rows]
    
    @classmethod
    def fetch_by_criteria(cls, col_name: str, criteria: str | int):
        sql = query_gen("select", cls.table_def, [col_name])
        db_row = CURSOR.execute(sql, (criteria,)).fetchone()
        if db_row:
            return cls.parse_db_row(db_row)
        return None
    
    def members(self):
        from models.member import Member
        sql = query_gen("select", Member.table_def, ["team_id"])
        db_rows = CURSOR.execute(sql, (self.id,),).fetchall()
        return [Member.parse_db_row(row) for row in db_rows]
    
    def has_member(self, member_id):
        return any(
            getattr(item, "member_id", None) == member_id 
            for item in self.members().values()
        )
    
    def assign_captain(self, member_id):
        if self.captain_id == member_id:
            raise Exception(
                f"Member '{member_id}' is already the team's captain")
        
        if not self.has_member(member_id):
            raise ValueError(
                f"Member '{member_id}' is not assigned to team '{self.id}'")
        
        self.captain_id = member_id
        self.update()
    
    def vacate_captain(self):
        if self.captain_id:
            self.captain_id = None
            self.update()
            
    def isFull(self):
        return len(self.members()) >= Team.member_cap
    
    @classmethod
    def exists(cls, team_id):
        return cls.fetch_by_criteria("team_id", team_id) is not None