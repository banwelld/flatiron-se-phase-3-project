from __init__ import CURSOR, CONN
import re

class Team():
    
    all = {}
        
    def __init__(
        self,
        name: str,
        captain_id: int | None = None,
        member_cap: int = 5,
        id: int | None = None
    ):
        self.name = name
        self.captain_id = captain_id
        self._member_cap = int(member_cap)
        self.id = id
                
    def __str__(self):
        return f"{type(self).__name__.upper()}: {self.name}"
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if not 5 <= len(name) <= 30:
            raise ValueError(
                f"Name '{name}' length is invalid, expected between 2 "
                f"and 20 characters, but got {len(name)}"
            )
            
        anomaly = re.search(r"[^a-zA-Z '.\-]", name).group()
        if anomaly is not None:
            raise ValueError(
                f"'{name}' contains invalid character '{anomaly}', "
                f"only letters, periods, hyphens, or apostrophes are allowed"
            )
        
        self._name = name
    
    @property
    def captain_id(self):
        return self._captain_id
    
    @captain_id.setter
    def captain_id(self, captain_id):
        id_list = [member.id for member in self.members()]
        if captain_id not in id_list:
            raise ValueError(
                f"ID '{captain_id}' does not belong to a current team member")
        self._captain_id = captain_id
        
    @property
    def member_cap(self):
        return self._member_cap
    
    @classmethod
    def create_table(cls):
        """Create a database table to house the team data.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT,
            captain_id INTEGER,
            member_cap INTEGER,
            FOREIGN KEY (captain_id) REFERENCES members(id_)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        """Drop the database table housing team data.
        """
        sql = """
            DROP TABLE IF EXISTS teams
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    def save(self):
        """Save team data to the database, add id number to the team object's
        id attribute, and add the team to Team.all.
        """
        sql = """
            INSERT INTO teams (name, captain_id, member_cap)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.captain_id, self.member_cap))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        """Persist team attribute updates to the team's database record.
        """
        sql = """
            UPDATE teams
            SET name = ?, captain_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.captain_id, self.id))
        CONN.commit()
        
    @classmethod
    def create(self, name: str, captain_id: int = 0):
        """Initialize a team object and save the team data to the database.
        """
        team = Team(name, captain_id)
        team.save()
        return team
    
    def delete(self):
        """Expunge team record from database, change team_id to None
        for all team members and remove instance from Team.all
        """
        sql = """
            DELETE FROM teams
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,),)
        CONN.commit()
        
        for member in self.members():
            self.remove_member(member.id)
                
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """Reconstitute a team instance from the team's database record.
        """
        if team := cls.all.get(record[0]):
            team.name = record[1]
            team.captain_id = record[2]
            team._member_cap = record[3]
        else:
            team = cls(record[1], record[2], record[3])
            team.id = record[0]
            cls.all[team.id] = team
        return team
    
    @classmethod
    def fetch_all(cls):
        """Fetch all team records from database and return as a list
        """
        sql = """
            SELECT *
            FROM teams
        """
        data = CURSOR.execute(sql).fetchall()
        return [cls.parse_db_row(row) for row in data]
    
    @classmethod
    def fetch_by_id(cls, id: int):
        """Fetch the first record from the database matching the id.
        """
        sql = """
            SELECT *
            FROM teams
            WHERE id = ?
        """
        data = CURSOR.execute(sql, (id,)).fetchone()
        return cls.parse_db_row(data) or None
    
    @classmethod
    def fetch_by_name(cls, name: str):
        """Fetch the first record from the database matching the
        team name.
        """
        sql = """
            SELECT *
            FROM teams
            WHERE name = ?
        """
        data = CURSOR.execute(sql, (name,)).fetchone()
        return cls.parse_db_row(data) or None
    
    def members(self):
        """Return a list of all members of the team instance or
        return an empty list if team has no members
        """
        from models.member import Member

        sql = """
            SELECT *
            FROM members
            WHERE team_id = ?
        """
        data = CURSOR.execute(sql, (self.id,),).fetchall()
        return [Member.parse_db_row(row) for row in data]
    
    def has_member(self, member_id):
        """Return boolean True/False depending on whether the member_id
        passed as an argument is assigned to the team
        """
        return any(
            getattr(item, "member_id", None) == member_id 
            for item in self.members().values()
        )
    
    def assign_captain(self, member_id):
        if self.has_member(member_id):
            self.captain_id = member_id
        else:
            raise ValueError(
                f"Member '{member_id}' is not assigned to team '{self.id}'")
    
    def vacate_captain(self):
        """Change the team's captain_id to None to vacate the position.
        """
        if self.captain_id:
            self.captain_id = None
            self.update()
            
    def isFull(self):
        """Indicates that a team membership has met its member cap"""
        return True if len(self.members()) >= self.member_cap else False
