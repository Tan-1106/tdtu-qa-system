from typing import List, Optional
from pydantic import BaseModel, Field

class PopularQuestion(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    question: str
    answer: str
    source_docs: List[str] = Field(default_factory=list)
    asked_count: int = 0
    
    class Config:
        populate_by_name = True