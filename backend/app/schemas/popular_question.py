from typing import List, Optional
from pydantic import BaseModel, Field

class PopularQuestionCreate(BaseModel):
    question: str
    answer: str
    source_docs: List[str]

class PopularQuestionUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    source_docs: Optional[List[str]] = None
    asked_count: Optional[int] = None

class PopularQuestionResponse(BaseModel):
    id: str = Field(default=None, alias="_id")
    question: str
    answer: str
    source_docs: List[str]
    asked_count: int = Field(default=0)

    class Config:
        orm_mode = True
        populate_by_name = True
