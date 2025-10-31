from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field

# Question Embedding Metadata Schema
class QuestionEmbeddingMetadata(BaseModel):
    doc_id: str = Field(..., description="ID of the associated document")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
# Import Question Embedding Schema
class QuestionEmbeddingImport(BaseModel):
    id: str = Field(..., description="Unique identifier for the question embedding")
    vector: List[float] = Field(..., description="The embedding vector")
    metadata: QuestionEmbeddingMetadata = Field(..., description="Metadata associated with the question embedding")

# Create Document Schema
class QuestionEmbeddingCreate(BaseModel):
    vector: List[float] = Field(..., description="The embedding vector")
    metadata: QuestionEmbeddingMetadata = Field(..., description="Metadata associated with the question embedding")

    class Config:
        from_attributes = True
        extra = "forbid"
        
# Question Embedding Response Schema
class QuestionEmbeddingResponse(BaseModel):
    id: str
    vector: List[float]
    metadata: QuestionEmbeddingMetadata

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }