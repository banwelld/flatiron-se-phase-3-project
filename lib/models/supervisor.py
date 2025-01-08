from models.employee import Employee
from models.agent import Agent
from models.department import Department
from models.call_review import CallReview
from validators import validate_object

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
        self._department = department
        Supervisor.all.append(self)
        
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
    
    def direct_reports_agent(self):
        return [
            agent for agent in Agent.all
            if agent.department == self.department
        ]
        
    def direct_reports_employee(self):
        return [
            agent.employee for agent in Agent.all
            if agent.department == self.department
        ]
    
    def reviews_delivered(self):
        return [
            review for review in CallReview.all
            if review.supervisor == self.employee
        ]
        
    def agent_reviews(self):
        return [
            review for review in CallReview.all
            if review.agent in self.direct_reports_employee()
        ]
        
    def new_review(
        self,
        agent: Employee,
        date: str,
        quality_score: int,
        adherence_score: int
    ) -> CallReview:
        return CallReview(
            agent, self.employee, date, quality_score, adherence_score
        )