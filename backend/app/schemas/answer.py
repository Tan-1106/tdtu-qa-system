from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone

class AnswerCreate(BaseModel):
    question_id: str
    content: str
    source_docs: List[str]

class AnswerUpdate(BaseModel):
    question_id: Optional[str] = None
    content: Optional[str] = None
    source_docs: Optional[List[str]] = None
    feedback: Optional[str] = None

class AnswerResponse(BaseModel):
    id: str = Field(default=None, alias="_id")
    question_id: str
    content: str
    source_docs: List[str]
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        populate_by_name = True