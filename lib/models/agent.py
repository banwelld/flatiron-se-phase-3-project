from models.employee import Employee
from models.department import Department
from models.call_review import CallReview
from helpers import validate_object

class Agent():
    
    all = []
    
    def __init__(
        self,
        employee: Employee,
        department: Department,
        bilingual: bool = False,
        agent_id: int = None
    ):
        self.employee = employee
        validate_object(department, Department)
        self._department = department
        self._bilingual = bilingual
        Agent.all.append(self)
        
        
    def __str__(self):
        return (
            f"{type(self).__name__}: {self.employee.fullname()} "
            f"({self.department.name} department)"
        )
        
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
    
    @property
    def bilingual(self):
        return self._bilingual
    
    def reviews(self):
        return [
            review for review in CallReview.all
            if review.agent == self.employee
        ]
        
    def quality_rating(self):
        scores = [review._quality_score for review in self.reviews()]
        quality = int(sum(scores) / len(scores) / 20 * 100)
        return f"{quality}%"
    
    def adherence_rating(self):
        scores = [review._adherence_score for review in self.reviews()]
        adherence = int(sum(scores) / len(scores) / 10 * 100)
        return f"{adherence}%"