from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Answer(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    question_id: str
    content: str
    source_docs: List[str] = Field(default_factory=list)
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True