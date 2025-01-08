from models.member import Member
from validators import validate_name, validate_object

class Team():
    
    all = []
        
    def __init__(
        self,
        name: str,
        captain: Member,
        member_limit: int = 5,
        team_id: int = None
    ):
        self.name = name
        self.captain = captain
        self._member_limit = int(member_limit)
        Team.all.append(self)
                
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
    def member_limit(self):
        return self._member_limit
    
    def members(self):
        return [item for item in Member.all if item.team_id == self.team_id]
    
    def member_count(self):
        return len(self.members())

    def add_new_member(self, first_name, last_name, birth_date):
        if self.member_count() < self._member_limit:
            return Member(first_name, last_name, birth_date, self)
        else:
            raise OverflowError(
                f"{type(self).__name__} '{self.name}' is full and cannot "
                "accept new members")
    