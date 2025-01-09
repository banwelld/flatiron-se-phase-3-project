from __init__ import CURSOR, CONN
from validators import validate_date, validate_name

class Member():
    
    all = []
    
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
        validate_date(birth_date)
        self._birth_date = birth_date
        self.team_id = int(team_id)
        self.id = int(id)
        
    def __str__(self):
        return f"{type(self).__name__.upper()}: {self.fullname()} ({self.team.name})"
        
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, first_name):
        validate_name(first_name, 20)
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        validate_name(last_name, 20)
        self._last_name = last_name
        
    @property
    def birth_date(self):
        return self._birth_date
    
    @classmethod
    def create_table(cls):
        """Create a database table to persist the member data.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT
            birth_date TEXT,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        """Drop the database table where member data is persisted.
        """
        sql = """
            DROP TABLE IF EXISTS members
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    def save(self):
        """Save member data to the database, add the newly-generated
        id number to the member object's id attribute, and add
        the member to Member.all
        """
        sql = """
            INSERT INTO members (first_name, last_name, birth_date, team_id)
            VALUES (?, ?, ?, ?)
        """
        CURSOR.execute(sql, (
            self.first_name, self.last_name, self.birth_date, self.team_id))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    def update(self):
        """Persist updates to member data to the member's record in the
        database.
        """
        sql = """
            UPDATE members
            SET first_name = ?, last_name = ?, birth_date = ?, team_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (
            self.first_name, 
            self.last_name, 
            self.birth_date, 
            self.team_id, 
            self.id))
        
        CONN.commit()
        
    @classmethod
    def create(
        self, 
        first_name: str, 
        last_name: str, 
        birth_date: str, 
        team_id: int
    ):
        """Initialize a member object and save the member data to the database.
        """
        member = Member(first_name, last_name, birth_date, team_id)
        member.save()
        return member
    
    def delete(self):
        """Expunge member record from database and from Member.all
        """
        sql = """
            DELETE FROM members
            WHERE id = ?
        """
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
            member.birth_date = record[3]
            member.team_id = record[4]
        else:
            member = cls(record[1], record[2], record[3], record[4])
            member.id = record[0]
            cls.all[member.id] = member
        return member
    
    @classmethod
    def fetch_whole_table(cls):
        """Fetch all member records from database and return as a list
        """
        sql = """
            SELECT *
            FROM members
        """
        data = CURSOR.execute(sql).fetchall()
        
        return [cls.parse_db_row(row) for row in data]
    
    @classmethod
    def fetch_by_id(cls, id: int):
        """Fetch the first record from the members table matching the id.
        """
        sql = """
            SELECT *
            FROM teams
            WHERE id = ?
        """
        data = CURSOR.execute(sql, (id,)).fetchone()
        
        return cls.parse_db_row(data) or None
    
    @classmethod
    def fetch_by_name(cls, first_name: str, last_name: str):
        """Fetch the first record from the members table matching the
        member name.
        """
        sql = """
            SELECT *
            FROM teams
            WHERE first_name = ? AND last_name = ?
        """
        data = CURSOR.execute(sql, (first_name, last_name)).fetchone()
        
        return cls.parse_db_row(data) or None
    