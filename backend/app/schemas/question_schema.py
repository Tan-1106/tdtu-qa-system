from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Create Question Schema
class QuestionCreate(BaseModel):
    question: str = Field(..., description="The question content")
    
    class Config:
        from_attributes = True
        extra = "forbid"


# Update Question Schem
class QuestionUpdate(BaseModel):
    status: str = Field(..., description="Status of the question")
    answer: Optional[str] = Field(None, description="Answer to the question")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Feedback Schema
class LeaveFeedback(BaseModel):
    feedback: str = Field(..., description="User feedback on the answer")

    class Config:
        from_attributes = True
        extra = "forbid"


# Question Response Schema
class QuestionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    status: str
    answer: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }