from validators import validate_date, validate_name

class Member():
    
    all = []
    
    def __init__(
        self, 
        first_name: str, 
        last_name: str, 
        birth_date: str, 
        team_id = None, 
        mem_id = None
    ):
        self.first_name = first_name
        self.last_name = last_name
        validate_date(birth_date)
        self._birth_date = birth_date
        self.team_id = team_id
        self.mem_id = mem_id
        
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
    def hire_date(self):
        return self._hire_date

    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    
    