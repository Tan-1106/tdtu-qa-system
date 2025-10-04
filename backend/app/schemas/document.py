from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Document Schema
class DocumentCreate(BaseModel):
    title: str = Field(..., description="Title of the document")
    doc_type: str = Field(default="", description="Type of the document")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the document")
    language: List[str] = Field(default_factory=lambda: ["vi"], description="Language of the document (default: vi)")
    file_url: HttpUrl = Field(..., description="File URL of the document")
    
    class Config:
        orm_mode = True
        extra = "forbid"

# Update Document Schema
class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the document")
    doc_type: Optional[str] = Field(default=None, description="Type of the document")
    tags: Optional[List[str]] = Field(default=None, description="Tags associated with the document")
    language: Optional[List[str]] = Field(default=None, description="Language of the document")
    file_url: Optional[HttpUrl] = Field(default=None, description="File URL of the document")

    class Config:
        orm_mode = True
        extra = "forbid"

# Document Response Schema
class DocumentResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    chunks: List[str]
    doc_type: str
    tags: List[str]
    language: List[str]
    file_url: HttpUrl
    uploaded_by: str
    edited_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }