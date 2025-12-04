from enum import Enum
from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# API Key Record Schema
class APIKeyRecord(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    api_key: str
    provider: str
    is_using: bool
    using_model: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        

#  API Key Creation Schema
class APIKeyCreationSchema(BaseModel):
    name: str
    description: Optional[str] = None
    api_key: str
    provider: str
    class Config:
        from_attributes = True
        extra = "forbid"    
        
        
# API Key Update Schema
class APIKeyInformationUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# API Key Usage Toggle Schema
class APIKeyAddModelSchema(BaseModel):
    using_model: str
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Enum for API Key Providers
class APIKeyProvider(str, Enum):
    OPENAI = "OpenAI"
    GEMINI = "Google"
    
    
# Get Available Models Schema
class GetAvailableModelsSchema(BaseModel):
    api_key: str
    provider: str
    class Config:
        from_attributes = True
        extra = "forbid"