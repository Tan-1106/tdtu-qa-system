from typing import Optional
from app.services import model_service
from app.schemas import api_key_schema
from app.utils.api_response import UserError


# Create a new API key
async def create_api_key(data: dict):
    api_provider = data["provider"]
    if api_provider not in [provider.value for provider in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([provider.value for provider in api_key_schema.APIKeyProvider]))
    
    api_key = await model_service.create_api_key(data)
    return api_key


# Get all API keys
async def get_all_api_keys(page: int, limit: int):
    api_keys = await model_service.get_all_api_keys(page, limit)
    return api_keys


# Update an existing API key
async def update_api_key(key_id: str, update_data: dict):
    if update_data == {}:
        raise UserError("No data provided for update.")
    
    if "provider" in update_data and update_data["provider"] not in [provider.value for provider in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([provider.value for provider in api_key_schema.APIKeyProvider]))
    
    
    updated_key = await model_service.update_api_key(key_id, update_data)
    return updated_key


# Delete an API key
async def delete_api_key(key_id: str):
    await model_service.delete_api_key(key_id)
    
    
# Toggle API Key Usage Status
async def toggle_api_key_status(key_id: str, using_model: str | None = None):
    updated_key = await model_service.toggle_api_key_status(key_id, using_model)
    return updated_key


# Get all available models
async def get_available_models(request: dict):
    provider = request["provider"]
    if provider not in [prov.value for prov in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([prov.value for prov in api_key_schema.APIKeyProvider]))
    
    models = await model_service.get_available_models(request)
    return models