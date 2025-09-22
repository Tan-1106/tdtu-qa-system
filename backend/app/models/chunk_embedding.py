from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ChunkMetadata(BaseModel):
    doc_id: str = Field(...)
    chunk_index: int = Field(...)
    doc_type: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = Field(default="vi")
    file_url: Optional[str] = Field(default=None)
    uploaded_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChunkEmbedding(BaseModel):
    embedding: List[float]
    metadata: ChunkMetadata

    class Config:
        arbitrary_types_allowed = True
