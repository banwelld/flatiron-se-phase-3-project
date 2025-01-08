from models.employee import Employee
from helpers import validate_date, validate_score, validate_object

class CallReview():
    
    all = []
    
    def __init__(
        self, 
        agent: Employee,
        supervisor: Employee,
        review_date: str, 
        quality_score: int,
        adherence_score: int, 
        review_id_=None
    ):
        validate_object(agent, Employee)
        validate_object(supervisor, Employee)
        validate_date(review_date)
        validate_score(quality_score, 20)
        validate_score(adherence_score, 10)
        
        self._agent = agent
        self._supervisor = supervisor
        self._review_date = review_date
        self._score_quality = quality_score
        self._score_adherence = adherence_score
        CallReview.all.append(self)
        
    def __str__(self):
        return f"{type(self).__name__}"
        
    @property
    def agent(self):
        return self._agent
    
    @property
    def supervisor(self):
        return self._supervisor
    
    @property
    def review_date(self):
        return self._review_date
    
    @property
    def score_quality(self):
        return self._quality_score
   
    @property
    def score_adherence(self):
        return self._adherence_score