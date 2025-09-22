from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ChunkMetadata(BaseModel):
    doc_id: str
    chunk_index: int
    doc_type: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    language: Optional[str] = "vi"
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChunkEmbedding(BaseModel):
    id: Optional[str] = None
    embedding: List[float] = Field(default_factory=list)
    metadata: ChunkMetadata

    class Config:
        arbitrary_types_allowed = True
