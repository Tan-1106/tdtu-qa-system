from typing import List, Optional
from pydantic import BaseModel, Field

class PopularQuestion(BaseModel):
    question: str = Field(...)
    answer: str = Field(...)
    source_docs: List[str] = Field(default_factory=list)
    asked_count: int = Field(default=0)

    class Config:
        populate_by_name = True