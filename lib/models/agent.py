from models.employee import Employee
from models.department import Department

class Agent(Employee):
    
    all = []
    
    def __init__(
        self,
        first_name: str,
        last_name: str,
        hire_date: str,
        department: Department,
        bilingual: bool = False,
        employee_id: int = None
    ):
        super().__init__(first_name, last_name, hire_date)
        self.department = department
        self.bilingual = bilingual
        Agent.all.append(self)
        
        
    def __str__(self):
        return f"{type(self).__name__}"
        
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, employee_id):
        validate_id(employee_id, str, 1, 20)
        self._employee_id = employee_id
    
    @property
    def supervisor_id(self):
        return self._supervisor_id
    
    @supervisor_id.setter
    def supervisor_id(self, supervisor_id):
        validate_id(supervisor_id, str, 1, 30)
        self._supervisor_id = supervisor_id