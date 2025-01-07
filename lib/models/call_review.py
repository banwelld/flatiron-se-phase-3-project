from agent import Agent
from helpers import validate_date, validate_object, validate_with_limits

class CallReview():
    
    all = []
    
    def __init__(
        self, 
        agent: Agent, 
        review_date: str, 
        score_quality: int,
        score_adherence: int, 
        id_=None
    ):
        validate_object(agent)
        validate_date(review_date)
        validate_with_limits(score_quality, int, 0, 20)
        validate_with_limits(score_adherence,int,  0, 10
                             )
        self._agent = agent
        self._review_date = review_date
        self._score_quality = score_quality
        self._score_adherence = score_adherence
        CallReview.all.append(self)
        
    def __str__(self):
        return f"{type(self).__name__}: {self.agent.name_last_first}, {self.review_date}"
        
    @property
    def agent(self):
        return self._agent
    
    @property
    def review_date(self):
        return self._review_date
    
    @property
    def score_quality(self):
        return self._score_quality
   
    @property
    def score_adherence(self):
        return self._score_adherence