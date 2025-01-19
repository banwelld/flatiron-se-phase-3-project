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

class Team():
    
    all = {}
    
    _table_def = PS["Team"]["table_def"]
        
    def __init__(
        self,
        name: str,
        captain: object = None,
        id: int | None = None
    ):
        self.name = name
        self.captain = captain
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
    def captain(self):
        return self._captain
    
    @captain.setter
    def captain(self, captain):
        self._captain = captain
    
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
            captain=self.captain
        )
        
        self.id = new_team_id
        type(self).all[self.id] = self
    
    def update(self):
        write_data(
            Team._table_def,
            self.id,
            name=self.name,
            captain=self.captain
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
        """
        Reconstitute a team instance from the team's record in the
        teams table.
        """
        from models.member import Member
        captain_obj = Member.fetch_by_id(record[2]) if record[2] else None
        if team := cls.all.get(record[0]):
            team.name = record[1]
            team.captain = captain_obj
        else:
            team = cls(record[1], captain_obj)
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
    
    @classmethod
    def fetch_by_id(cls, id: int):
        result = cls.fetch_rows(id=id)[0]
        return result
    
    @classmethod
    def list_by_id(cls):
        teams = cls.fetch_rows()
        return [team.id for team in teams]
        
    def members(self):
        from models.member import Member
        return Member.fetch_rows(team=self)
    
    def has_member(self, member_obj):
        return any(member == member_obj for member in self.members())
    
    def install_captain(self, member_obj):
        if not self.has_member(member_obj):
            raise ValueError(
                f"Member '{member_obj.id}' is not assigned to team "
                f"'{self.id}'"
            )
        self.captain = member_obj
        self.update()
    
    def dump_captain(self):
        if self.captain:
            self.captain = None
            self.update()