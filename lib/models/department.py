from models.supervisor import Supervisor
from models.agent import Agent
from validators import validate_name

class Department():
    
    all = []
    
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        validate_name(name, 12)
        self._name = name

