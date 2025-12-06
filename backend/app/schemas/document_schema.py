from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# Document Record Schema
class DocumentRecord(BaseModel):
    id: str = Field(alias="_id")
    file_name: str
    doc_type: str
    department: Optional[str] = None
    faculty: Optional[str] = None
    file_url: HttpUrl
    file_path: str
    uploaded_by: str
    uploaded_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        
        
# Document Upload Schema
class DocumentUploadSchema(BaseModel):
    doc_type: str
    department: Optional[str] = None
    faculty: Optional[str] = None
    file_url: HttpUrl
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Document Update Schema
class DocumentUpdateSchema(BaseModel):
    file_name: Optional[str] = None
    doc_type: Optional[str] = None
    department: Optional[str] = None
    faculty: Optional[str] = None
    file_url: Optional[HttpUrl] = None
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Add Document Chunk Schema
class UpdateChunkQuestionSchema(BaseModel):
    question: str
    class Config:
        from_attributes = True
        extra = "forbid"