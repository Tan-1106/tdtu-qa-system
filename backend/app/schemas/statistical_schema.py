from enum import Enum
from typing import Optional
from pydantic import BaseModel


class PeriodType(str, Enum):
    Weekly = "Weekly"
    Monthly = "Monthly"
    Yearly = "Yearly"
    
    
class AssignFacultyScopeRequestSchema(BaseModel):
    faculty: str
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
class UpdatePopularQuestionRequestSchema(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    class Config:
        from_attributes = True
        extra = "forbid"