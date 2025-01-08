from models.member import Member
from models.department import Department
from models.call_review import CallReview
from validators import validate_object

class Agent():
    
    all = []
    
    def __init__(
        self,
        member: Member,
        department: Department,
        bilingual: bool = False,
        agent_id: int = None
    ):
        self.member = member
        validate_object(department, Department)
        self._department = department
        self._bilingual = bilingual
        Agent.all.append(self)
        
        
    def __str__(self):
        return (
            f"{type(self).__name__}: {self.member.fullname()} "
            f"({self.department.name} department)"
        )
        
    @property
    def member(self):
        return self._member
    
    @member.setter
    def member(self, member):
        validate_object(member, Member)
        self._member = member
    
    @property
    def department(self):
        return self._department
    
    @property
    def bilingual(self):
        return self._bilingual
    
    def reviews(self):
        return [
            review for review in CallReview.all
            if review.agent == self.member
        ]
        
    def quality_rating(self):
        scores = [review._quality_score for review in self.reviews()]
        quality = int(sum(scores) / len(scores) / 20 * 100)
        return f"{quality}%"
    
    def adherence_rating(self):
        scores = [review._adherence_score for review in self.reviews()]
        adherence = int(sum(scores) / len(scores) / 10 * 100)
        return f"{adherence}%"