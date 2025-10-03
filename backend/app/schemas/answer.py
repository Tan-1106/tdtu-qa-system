from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Answer Schema
class AnswerCreate(BaseModel):
    question_id: str = Field(..., description="Question ID associated with the answer")
    answer: str = Field(..., description="The answer content")
    source_docs: List[str] = Field(..., description="List of source document IDs")

    class Config:
        orm_mode = True
        extra = "forbid"
        
# Update feedback of Answer Schema
class AnswerFeedbackUpdate(BaseModel):
    feedback: Optional[str] = Field(default=None, description="Feedback on the answer (Like/Dislike)")

    class Config:
        orm_mode = True
        extra = "forbid"
        
# Answer Response Schema
class AnswerResponse(BaseModel):
    id: str = Field(alias="_id")
    question_id: str
    answer: str
    source_docs: List[str]
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }