from program_settings import PROGRAM_SETTINGS as PS
from utility import (
    check_within_limits as limits,
    check_characters as chars,
    create_table,
    drop_table,
    write_data,
    delete_row,
    select_rows
)

# TODO: finish Team.members()

class Team():
    
    all = {}
    
    _table_def = PS["Team"]["table_def"]
        
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
        limits(length, 4, 30)
        chars(name, r"[^a-zA-Z '.\-]")
        self._name = name
    
    @property
    def captain_id(self):
        return self._captain_id
    
    @captain_id.setter
    def captain_id(self, captain_id):
        if captain_id is not None:
            
            if self.captain_id:
                
                if self.captain_id == captain_id:
                    raise Exception(
                        "Specified member is already the team's captain.")
                
                raise PermissionError(
                    "Cannot overwrite captain assignment. Please remove current "
                    "captain before assigning a new one."
                )
                
        self._captain_id = captain_id
    
    @classmethod
    def build_table(cls):
        create_table(cls._table_def)
        
    @classmethod
    def delete_table(cls):
        drop_table(cls._table_def)
        
    def save(self):
        new_team_id = write_data(
            Team._table_def,
            name=self.name,
            captain_id=self.captain_id
        )
        
        self.id = new_team_id
        type(self).all[self.id] = self
    
    def update(self):
        write_data(
            Team._table_def,
            self.id,
            name=self.name,
            captain_id=self.captain_id
        )
        
    @classmethod
    def create(cls, name: str):
        cls.build_table
        team = cls(name)
        team.save()
        return team
    
    def delete(self):
        for mem in self.members():
            mem.leave_current_team()
        delete_row(Team._table_def, self.id)
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
    def fetch_rows(cls, **params):
        """
        Fetches all matching records from the 'teams' table, filtered
        based the 'params' keyword arguments, if any. Returns a list of
        all matching team instances or empty list if none found.
        """
        db_data = select_rows(cls._table_def, **params)
        teams = [cls.parse_db_row(row) for row in db_data]
        return teams
    
    def members(self):
        from models.member import Member
        return Member.fetch_rows(team_id=self.id)
    
    def has_member(self, member_id):
        return any(member.id == member_id for member in self.members())
    
    def install_captain(self, member_id):
        if not self.has_member(member_id):
            raise ValueError(
                f"Member '{member_id}' is not assigned to team '{self.id}'")
        self.captain_id = member_id
        self.update()
    
    def dump_captain(self):
        if self.captain_id:
            self.captain_id = None
            self.update()