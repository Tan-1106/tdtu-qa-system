from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field

# Create Prototype Schema
class PrototypeCreate(BaseModel):
    id: str = Field(..., description="ID of the prototype")
    centroid_vector: List[float] = Field(..., description="The centroid embedding vector")
    question_embedding_ids: List[str] = Field(..., description="List of question embedding IDs clustered in this prototype")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Update Prototype Centroid Schema
class PrototypeCentroidUpdate(BaseModel):
    centroid_vector: List[float] = Field(..., description="The centroid embedding vector")

    class Config:
        orm_mode = True
        extra = "forbid"

# Update Prototype Question Embeddings Schema
class PrototypeQuestionEmbeddingsUpdate(BaseModel):
    question_embedding_ids: List[str] = Field(..., description="List of question embedding IDs clustered in this prototype")

    class Config:
        orm_mode = True
        extra = "forbid"

# Add/Remove Question Embedding ID Schema
class PrototypeQuestionEmbeddingIDUpdate(BaseModel):
    question_embedding_id: str = Field(..., description="ID of the question embedding")

    class Config:
        orm_mode = True
        extra = "forbid"
        
# Prototype Response Schema
class PrototypeResponse(BaseModel):
    id: str = Field(alias="_id")
    centroid_vector: List[float]
    question_embedding_ids: List[str]

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }