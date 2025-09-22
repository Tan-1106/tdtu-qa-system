from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Document(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    content: str
    chunks: List[str]
    embedding_ids: List[str]
    doc_type: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = "vi"
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 
    
    class Config:
        populate_by_name = True