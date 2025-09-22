from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Document(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    chunks: List[str] = Field(default_factory=list)
    embedding_ids: List[str] = Field(default_factory=list)
    doc_type: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = Field(default="vi")
    file_url: Optional[str] = Field(default=None)
    uploaded_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True