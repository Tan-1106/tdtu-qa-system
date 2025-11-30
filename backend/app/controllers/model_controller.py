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
    api_provider = update_data["provider"]
    if api_provider and api_provider not in [provider.value for provider in api_key_schema.APIKeyProvider]:
        raise UserError("Invalid API key provider. Supported providers are: " + ", ".join([provider.value for provider in api_key_schema.APIKeyProvider]))
    
    update_data = {k: v for k, v in update_data.items() if v is not None}
    updated_key = await model_service.update_api_key(key_id, update_data)
    return updated_key