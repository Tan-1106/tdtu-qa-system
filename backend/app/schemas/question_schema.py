from bson import ObjectId
from datetime import datetime
from typing import List, Optional
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
    answer_id: Optional[str] = Field(default=None, description="Answer ID associated with the question")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
# Update Normalized Question Schema
class QuestionNormalizedUpdate(BaseModel):
    normalized_question: List[str] = Field(..., description="Updated normalized version of the question")
    
    class Config:
        from_attributes = True
        extra = "forbid"

# Question Response Schema
class QuestionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    status: str
    answer_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }