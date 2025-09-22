from typing import List, Optional
from pydantic import BaseModel, Field

# Schema tạo PopularQuestion (request)
class PopularQuestionCreate(BaseModel):
    question: str
    answer: str
    source_docs: List[str]

# Schema cập nhật PopularQuestion (request)
class PopularQuestionUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    source_docs: Optional[List[str]] = None
    asked_count: Optional[int] = None

# Schema trả về PopularQuestion (response)
class PopularQuestionResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    question: str
    answer: str
    source_docs: List[str]
    asked_count: int = 0

    class Config:
        orm_mode = True
        populate_by_name = True
