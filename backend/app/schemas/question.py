from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class QuestionCreate(BaseModel):
    user_id: str
    question: str
    normalized_question: str
    status: Optional[str] = "pending"
    
class QuestionStatusUpdate(BaseModel):
    status: Optional[str] = "pending"

class QuestionResponse(BaseModel):
    id: str = Field(default=None, alias="_id")
    user_id: str
    question: str
    normalized_question: str
    created_at: datetime
    status: str
    answer_id: Optional[str] = None

    class Config:
        orm_mode = True
        populate_by_name = True