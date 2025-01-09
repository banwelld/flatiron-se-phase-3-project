from __init__ import CURSOR, CONN
from models.member import Member
from validators import validate_name, validate_object

class Team():
    
    all = {}
        
    def __init__(
        self,
        name: str,
        captain_id: int,
        member_cap: int = 5,
        id: int = None
    ):
        self.name = name
        self.captain_id = int(captain_id)
        self._member_cap = int(member_cap)
        self.id = int(id)
                
    def __str__(self):
        return (
            f"{type(self).__name__.upper()}: {self.name} "
            f"(Captain: {self.captain.fullname()})"
        )
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        validate_name(name, 30)
        self._name = name
    
    @property
    def captain(self):
        return self._member
    
    @captain.setter
    def captain(self, captain):
        validate_object(captain, Member)
        self._captain = captain
        
    @property
    def member_cap(self):
        return self._member_cap
    
    @classmethod
    def create_table(cls):
        """Create a database table to persist the team data.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT,
            captain_id INTEGER,
            member_cap INTEGER,
            FOREIGN KEY (captain_id) REFERENCES members(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        """Drop the database table where team data is persisted.
        """
        sql = """
            DROP TABLE IF EXISTS teams
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    def save(self):
        """Save team data to the database, add the newly-generated
        id number to the team object's id attribute, and add
        the team to Team.all
        """
        sql = """
            INSERT INTO teams (name, captain_id, member_cap)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.captain.mem_id, self.member_cap))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        """Persist updates to team data to the team's record in the
        database.
        """
        sql = """
            UPDATE teams
            SET name = ?, captain_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.captain_id, self.id))
        CONN.commit()
        
    @classmethod
    def create(self, name: str, captain_id: int):
        """Initialize a team object and save the team data to the database.
        
        Disallows customized member limits as this is only allowed to create
        special non-team teams.
        """
        team = Team(name, captain_id)
        team.save()
        return team
    
    def delete(self):
        """Expunge team record from database and from Team.all
        """
        sql = """
            DELETE FROM teams
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,),)
        CONN.commit()
                
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def parse_db_row(cls, record: list):
        """Reconstitute a team instance from the team's database record.
        """
        if team := cls.all.get(record[0]):
            team.name = record[1]
            team.captain_id = record[2]
            team.member_cap = record[3]
        else:
            team = cls(record[1], record[2], record[3])
            team.id = record[0]
            cls.all[team.id] = team
        return team
    
    @classmethod
    def fetch_whole_table(cls):
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
    