from __init__ import CURSOR, CONN
import re
from datetime import date

class Member():
    
    all = {}
    
    def __init__(
        self, 
        first_name: str,
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None, 
        id: int | None = None
    ):
        # validate date formet in birth_date

        date_match = re.match(r"^[0-9]{4}(/[0-9]{2}){2}$", birth_date)
        if date_match is None:
            raise ValueError(
                f"Date '{birth_date}' format invalid, expected 'YYYY/MM/DD'")
            
        #validate date value in birth_date
            
        date_yr = int(birth_date[:4])
        date_mon = int(birth_date[5:7])
        date_day = int(birth_date[8:])
        try:
            date(date_yr, date_mon, date_day)
        except ValueError:
            raise ValueError(
                f"Date '{birth_date}' invalid, check month/day combination")
        
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
        if not 2 <= len(first_name) <= 20:
            raise ValueError(
                f"Name '{first_name}' length is invalid, expected between 2 "
                f"and 20 characters, but got {len(first_name)}")
            
        anomaly = re.search(r"[^a-zA-Z '.\-]", first_name)
        if anomaly is not None:
            raise ValueError(
                f"'{first_name}' contains invalid character "
                f"'{anomaly.group()}', only letters, periods, hyphens, or "
                "apostrophes are allowed"
            )
            
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        if not 2 <= len(last_name) <= 20:
            raise ValueError(
                f"Name '{last_name}' length is invalid, expected between 2 "
                f"and 20 characters, but got {len(last_name)}")
            
        anomaly = re.search(r"[^a-zA-Z '.\-]", last_name)
        if anomaly is not None:
            raise ValueError(
                f"'{last_name}' contains invalid character "
                f"'{anomaly.group()}', only letters, periods, hyphens, or "
                "apostrophes are allowed"
            )

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
            from models.team import Team
            if team := Team.fetch_by_id(team_id):
                if team.isFull():
                    raise OverflowError(
                        f"Team with ID '{team_id}' has reached its "
                        "member limit.")
            
        self._team_id = team_id
    
    @classmethod
    def create_table(cls):
        """Create a database table to persist the member data.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
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
        """Adds member instance record to the members table in the
        database and assigns the record's primary key value as the
        member instance's id. Then adds the instance to Member.all.
        """
        sql = """
            INSERT INTO members (first_name, last_name, birth_date, team_id)
            VALUES (?, ?, ?, ?)
        """
        CURSOR.execute(sql, (
            self.first_name, self.last_name, self.birth_date, self.team_id))
        CONN.commit()
        
        self._id = CURSOR.lastrowid
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
        cls,
        first_name: str, 
        last_name: str, 
        birth_date: str, 
        team_id: int | None = None
    ):
        """Initialize a member object and save the member data to the database.
        """
        cls.create_table()  # only if not table exists
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
            member._birth_date = record[3]
            member.team_id = record[4] if record[4] else None
        else:
            member = Member(record[1], record[2], record[3], record[4])
            member.id = record[0]
            cls.all[member.id] = member
        return member
    
    @classmethod
    def fetch_all(cls):
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
            FROM members
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
            FROM members
            WHERE first_name = ? AND last_name = ?
        """
        data = CURSOR.execute(sql, (first_name, last_name)).fetchone()
        return cls.parse_db_row(data) or None
    
    def leave_current_team(self):
        """Assigns team_id attribute of None to the member instance. If
        the team instance to which the member instance was assigned has
        a captain_id attribute equal to the member inetance's id,
        invokes the vacate_captain() method on the team instance.
        Updates the database record after all changes made.
        
        Raises Exception if the member instance has team_id attribute
        equal to None.
        """
        if self.team_id is not None:
            from models.team import Team
            my_team = Team.fetch_by_id(self.team_id)
            if self.id == my_team.captain_id:
                my_team.vacate_captain()
            self.team_id = None
            self.update()
        else:
            raise Exception(
                f"Member '{self.id}' has no team_id attribute")
            
    def join_team(self, team_id: int):
        """Assigns the specified team_id attribute value to the member
        instance. If the member instance already has a valid team_id
        attribute, invokes the leave_current_team() method before
        assigning the specified team_id to the member instance.
        
        Raises ValueError for invalid team_id or Exception if member is
        already assigned to the specified team.
        """
        if self.team_id is not team_id:
            from models.team import Team
            if Team.fetch_all()[team_id]:
                if self.team_id is not None:
                    self.leave_current_team()
                self.team_id = team_id
                self.update()
            else:
                raise ValueError(f"'{team_id}' invalid team ID")
        else:
            raise Exception(
                f"Member '{self.id}' is already associated with team '{team_id}'")
    
    @classmethod
    def list_free_agents(cls):
        """Returns a list of member instances with team_id attributes
        having a value of None
        """
        return [
            member for member in cls.fetch_all()
            if member.team_id == None]