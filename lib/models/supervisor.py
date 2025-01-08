from models.employee import Employee
from models.department import Department
from helpers import validate_object

class Supervisor():
    
    all = []
    
    def __init__(
        self,
        employee: Employee,
        department: Department,
        employee_id: int = None
    ):
        self.employee = employee
        validate_object(department, Department)
        self.department = department
        Supervisor.all.append(self)
        
    def __str__(self):
        return f"{type(self).__name__}"
        
    @property
    def employee(self):
        return self._employee
    
    @employee.setter
    def employee(self, employee):
        validate_object(employee, Employee)
        self._employee = employee
    
    @property
    def department(self):
        return self._department
    