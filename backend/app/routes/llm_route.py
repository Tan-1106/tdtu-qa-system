from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import api_key_schema
from app.controllers import llm_controller
from app.utils.basic_information import Role
from app.utils.api_response import api_response


# --- ROUTER ---
router = APIRouter(
    prefix="/model",
    tags=["Model"],
    dependencies=[Depends(auth_service.require_role([Role.ADMIN.value]))]
)


# --- ROUTES ---
# Create a new API Key
@router.post("/api-keys")
async def create_api_key(data: api_key_schema.APIKeyCreationSchema):
    data = jsonable_encoder(data)
    api_key = await llm_controller.create_api_key(data)
    return api_response(
        status_code=201,
        message="API key created successfully.",
        details=jsonable_encoder(api_key)
    )


# Get all api keys
@router.get("/api-keys")
async def get_api_keys(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    provider: str = Query(None)
):
    api_keys = await llm_controller.get_all_api_keys(page=page, limit=limit, keyword=keyword, provider=provider)
    return api_response(
        status_code=200,
        message="Get API keys successfully.",
        details=api_keys
    )
    
    
# Get current using API Key
@router.get("/api-keys/current")
async def get_current_api_key():
    api_key = await llm_controller.get_current_api_key()
    return api_response(
        status_code=200,
        message="Get current API key successfully.",
        details=jsonable_encoder(api_key)
    )
    
    
# Get a single API Key by ID
@router.get("/api-keys/{key_id}")
async def get_api_key_by_id(key_id: str):
    api_key = await llm_controller.get_api_key_by_id(key_id)
    return api_response(
        status_code=200,
        message="Get API key successfully.",
        details=jsonable_encoder(api_key)
    )
    

# Update an API Key
@router.patch("/api-keys/{key_id}")
async def update_api_key_information(
    key_id: str,
    update_data: Optional[api_key_schema.APIKeyInformationUpdateSchema] = None
):
    if update_data:
        update_data = jsonable_encoder(update_data)
        update_data = {k: v for k, v in update_data.items() if v is not None}
    else:
        update_data = {}
    
    updated_key = await llm_controller.update_api_key(key_id, update_data)
    return api_response(
        status_code=200,
        message="API key updated successfully.",
        details=jsonable_encoder(updated_key)
    )
    
    
# Delete an API Key
@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str):
    await llm_controller.delete_api_key(key_id)
    return api_response(
        status_code=200,
        message="API key deleted successfully."
    )


# Toggle API Key Usage Status
@router.post("/api-keys/{key_id}/toggle-usage")
async def toggle_api_key_status(key_id: str):
    updated_key = await llm_controller.toggle_api_key_status(key_id)
    return api_response(
        status_code=200,
        message="API key usage status toggled successfully.",
        details=jsonable_encoder(updated_key)
    )
    
    
# Add or change using model for an API Key
@router.post("/api-keys/{key_id}/add-model")
async def add_model_to_api_key(
    key_id: str,
    data: api_key_schema.APIKeyAddModelSchema
):
    update_data = jsonable_encoder(data)
    updated_key = await llm_controller.update_api_key(key_id, update_data)
    return api_response(
        status_code=200,
        message="Using model added/updated successfully.",
        details=jsonable_encoder(updated_key)
    )
    
    
# Get all available models
@router.post("/available-models")
async def get_available_models(
    request: api_key_schema.GetAvailableModelsSchema
):
    request = jsonable_encoder(request)
    models = await llm_controller.get_available_models(request)
    return api_response(
        status_code=200,
        message="Get available models successfully.",
        details={"models": models}
    )