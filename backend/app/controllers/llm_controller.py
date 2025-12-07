from typing import Optional
from app.services import llm_service
from app.schemas import api_key_schema
from app.utils.api_response import UserError


# Create a new API key
async def create_api_key(data: dict):
    api_provider = data["provider"]
    if api_provider not in [provider.value for provider in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([provider.value for provider in api_key_schema.APIKeyProvider]))
    
    await llm_service.get_available_models(data)
    api_key = await llm_service.create_api_key(data)
    return api_key


# Get all API keys
async def get_all_api_keys(
    page: int, limit: int,
    keyword: Optional[str] = None,
    provider: Optional[str] = None
):
    if provider and provider not in [prov.value for prov in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([prov.value for prov in api_key_schema.APIKeyProvider]))
    
    api_keys = await llm_service.get_all_api_keys(page, limit, keyword, provider)
    return api_keys


# Get a single API key by ID
async def get_api_key_by_id(key_id: str):
    api_key = await llm_service.get_api_key_by_id(key_id)
    return api_key


# Get current using API key
async def get_current_api_key():
    api_key = await llm_service.get_current_api_key()
    return api_key


# Update an existing API key
async def update_api_key(
    key_id: str,
    update_data: dict
):
    if update_data == {}:
        raise UserError("No data provided for update.")
    
    updated_key = await llm_service.update_api_key(key_id, update_data)
    return updated_key


# Delete an API key
async def delete_api_key(key_id: str):
    await llm_service.delete_api_key(key_id)
    
    
# Toggle API Key Usage Status
async def toggle_api_key_status(key_id: str):
    updated_key = await llm_service.toggle_api_key_status(key_id)
    return updated_key


# Get all available models
async def get_available_models(request: dict):
    provider = request["provider"]
    if provider not in [prov.value for prov in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([prov.value for prov in api_key_schema.APIKeyProvider]))
    
    models = await llm_service.get_available_models(request)
    return models