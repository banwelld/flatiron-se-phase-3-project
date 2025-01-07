class Agent():
    
    all = []
    
    def __init__(self, name_first: str, name_last: str, date_hired: str, supervisor, id_=None):
        validate_date(date_hired)
        self.id = id_
        self.name_first = name_first
        self.name_last = name_last
        self._date_hired = date_hired
        self.supervisor = supervisor
        Agent.all.append(self)
        
    @property
    def name_first(self):
        return self._name_first
    
    @name_first.setter
    def name_first(self, name_first):
        validate_name(name_first)
        self._name_first = name_first
    
    @property
    def name_last(self):
        return self._name_last
    
    @name_last.setter
    def name_last(self, name_last):
        validate_name(name_last)
        self._name_last = name_last

    @property
    def date_hired(self):
        return self._date_hired
    
    @property
    def supervisor(self):
        return self._supervisor
    
    @supervisor.setter
    def supervisor(self, supervisor):
        validate_object(supervisor, Supervisor)
        self._supervisor = supervisor