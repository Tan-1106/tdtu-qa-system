from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Document(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    source: str
    content: str
    chunks:  Optional[List[str]] = []
    doc_type: Optional[str] = None
    language: Optional[str] = "vi"
    tags: Optional[List[str]] = None
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    embedding_ids: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 
    
    class Config:
        populate_by_name = True