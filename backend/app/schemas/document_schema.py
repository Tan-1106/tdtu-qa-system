from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Document Schema
class DocumentCreate(BaseModel):
    chunks: List[str] = Field(..., description="Text chunks of the document")
    doc_type: str = Field(default=..., description="Type of the document")
    department: str = Field(default=..., description="Department of the document")
    language: List[str] = Field(default_factory=lambda: ["vi"], description="Language of the document (default: vi)")
    file_url: HttpUrl = Field(..., description="File URL of the document")
    
    class Config:
        from_attributes = True
        extra = "forbid"


# Update Document Schema
class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the document")
    doc_type: Optional[str] = Field(default=None, description="Type of the document")
    department: Optional[str] = Field(default=None, description="Department of the document")
    language: Optional[List[str]] = Field(default=None, description="Language of the document")
    file_url: Optional[HttpUrl] = Field(default=None, description="File URL of the document")

    class Config:
        from_attributes = True
        extra = "forbid"


# Document Response Schema
class DocumentResponse(BaseModel):
    id: str = Field(alias="_id")
    file_path: Optional[str] = None
    title: str
    chunks: List[str]
    doc_type: str
    department: str
    language: List[str]
    file_url: HttpUrl
    uploaded_by: str
    edited_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        
        
# Document Chunk Response Schema
class DocumentChunkResponse(BaseModel):
    doc_id: str
    title: str
    chunk_index: int
    chunk_text: str
    file_url: HttpUrl

    class Config:
        from_attributes = True
        json_encoders = { ObjectId: str }