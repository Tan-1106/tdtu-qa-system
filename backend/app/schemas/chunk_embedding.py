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

class ChunkEmbeddingCreate(BaseModel):
    embedding: List[float]
    metadata: ChunkMetadata
    
class ChunkEmbeddingUpdate(BaseModel):
    embedding: Optional[List[float]] = None
    metadata: Optional[ChunkMetadata] = None

class ChunkEmbeddingResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    embedding: List[float]
    metadata: ChunkMetadata

    class Config:
        orm_mode = True
        populate_by_name = True