from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field

# Prototype Metadata Schema
class PrototypeMetadata(BaseModel):
    question_embedding_ids: List[str] = Field(..., description="List of question embedding IDs clustered in this prototype")
    
    class Config:
        from_attributes = True
        extra = "forbid"


# Create Prototype Schema
class PrototypeCreate(BaseModel):
    centroid_vector: List[float] = Field(..., description="The centroid embedding vector")
    metadata: PrototypeMetadata = Field(..., description="Metadata associated with the prototype")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Prototype Response Schema
class PrototypeResponse(BaseModel):
    id: str = Field(alias="_id")
    centroid_vector: List[float]
    metadata: PrototypeMetadata

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }