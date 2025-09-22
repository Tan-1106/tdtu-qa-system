from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone

# Schema để tạo answer (request)
class AnswerCreate(BaseModel):
    question_id: str
    content: str
    source_docs: List[str]

    @model_validator(mode="before")
    def check_content_and_source_docs(cls, values):
        content = values.get("content")
        source_docs = values.get("source_docs")
        if not content:
            raise ValueError("content không được để trống")
        if not source_docs or len(source_docs) == 0:
            raise ValueError("source_docs phải có ít nhất 1 chunk/document")
        return values

# Schema để cập nhật answer (request)
class AnswerUpdate(BaseModel):
    question_id: Optional[str] = None
    content: Optional[str] = None
    source_docs: Optional[List[str]] = None
    feedback: Optional[str] = None
    
    @model_validator(mode="before")
    def check_content_and_source_docs_if_present(cls, values):
        content = values.get("content")
        source_docs = values.get("source_docs")
        if "content" in values and (content is None or content.strip() == ""):
            raise ValueError("content không được để trống nếu được gửi")
        if "source_docs" in values and (not source_docs or len(source_docs) == 0):
            raise ValueError("source_docs phải có ít nhất 1 chunk/document nếu được gửi")
        return values

# Schema trả về answer (response)
class AnswerResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    question_id: str
    content: str
    source_docs: List[str]
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        populate_by_name = True