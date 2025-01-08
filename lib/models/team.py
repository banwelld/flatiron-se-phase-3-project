from models.member import Member
from validators import validate_object, validate_name

class Team():
    
    all = []
    
    def __init__(
        self,
        name: str,
        captain: str,
        id_: int = None
    ):
        self.name = name
        self.captain = captain
        Team.all.append(self)
        
    def __str__(self):
        return (
            f"{type(self).__name__}.upper(): {self.name} "
            f"(Captain: )"
        )
        
    @property
    def name(self):
        return self._department_name
    
    @name.setter
    def name(self, name):
        validate_name(name, 30)
        self._name = name
    
    @property
    def captain(self):
        return self._member
    
    @captain.setter
    def captain(self, captain):
        validate_name(captain, 5)
        self._captain = captain
        
    