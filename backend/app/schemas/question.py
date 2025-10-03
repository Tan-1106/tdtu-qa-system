from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Question Schema
class QuestionCreate(BaseModel):
    user_id: str = Field(..., description="User ID who asked the question")
    question: str = Field(..., description="The question content")
    normalized_question: List[str] = Field(..., description="Normalized version of the question")
    
    class Config:
        orm_mode = True
        extra = "forbid"

# Update Question Schema
class QuestionUpdate(BaseModel):
    status: str = Field(..., description="Status of the question")
    answer_id: Optional[str] = Field(default=None, description="Answer ID associated with the question")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Update Normalized Question Schema
class QuestionNormalizedUpdate(BaseModel):
    normalized_question: List[str] = Field(..., description="Updated normalized version of the question")
    
    class Config:
        orm_mode = True
        extra = "forbid"

# Question Response Schema
class QuestionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    normalized_question: List[str]
    status: str
    answer_id: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }