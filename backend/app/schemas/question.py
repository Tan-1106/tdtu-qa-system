from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

# Schema để tạo question (request)
class QuestionCreate(BaseModel):
    user_id: str
    question: str
    normalized_question: str
    status: Optional[str] = "pending"
    
# Schema để cập nhật question status (request)
class QuestionStatusUpdate(BaseModel):
    status: Optional[str] = "pending"

# Schema trả về question (response)
class QuestionResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    question: str
    normalized_question: str
    created_at: datetime
    status: str
    answer_id: Optional[str] = None

    class Config:
        orm_mode = True
        populate_by_name = True