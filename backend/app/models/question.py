from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Question(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    question: str
    normalized_question: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str
    answer_id: Optional[str] = None
    
    class Config:
        populate_by_name = True