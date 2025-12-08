from enum import Enum
from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Question Schema
class QuestionSchema(BaseModel):
    question: str
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Question Record Schema
class QARecordSchema(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    user_sub: str
    user_faculty: Optional[str] = None
    question: str
    answer: Optional[str] = None
    feedback: Optional[str] = None
    manager_answer: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        
        
# Feedback Enum
class Feedback(str, Enum):
    Like = "Like"
    Dislike = "Dislike"
    
    
# Feedback Schema
class FeedbackSchema(BaseModel):
    feedback: str
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Manager Answer Schema
class ManagerAnswerSchema(BaseModel):
    manager_answer: str
    class Config:
        from_attributes = True
        extra = "forbid"
