from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentCreate(BaseModel):
    title: str
    content: str
    chunks: List[str]
    embedding_ids: List[str]
    doc_type: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = "vi"
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    chunks: Optional[List[str]] = None
    embedding_ids: Optional[List[str]] = None
    doc_type: Optional[str] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str = Field(default=None, alias="_id")
    title: str
    content: str
    chunks: List[str]
    embedding_ids: List[str]
    doc_type: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = "vi"
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        populate_by_name = True
