from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Question(BaseModel):
    user_id: str = Field(...)
    question: str = Field(...)
    normalized_question: str = Field(...)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(...)
    answer_id: Optional[str] = Field(default=None)
    
    class Config:
        populate_by_name = True