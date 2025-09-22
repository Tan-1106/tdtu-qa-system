from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Answer(BaseModel):
    question_id: str = Field(...)
    content: str = Field(...)
    source_docs: List[str] = Field(default_factory=list)
    feedback: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True