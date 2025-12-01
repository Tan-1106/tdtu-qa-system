from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.utils.user_information import Role
from app.controllers import model_controller
from app.utils.api_response import api_response
from app.schemas import api_key_schema


# --- ROUTERS ---
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
    api_key = await model_controller.create_api_key(data)
    return api_response(
        status_code=201,
        message="API key created successfully.",
        details=jsonable_encoder(api_key)
    )


# Get all api keys
@router.get("/api-keys")
async def get_api_keys(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    api_keys = await model_controller.get_all_api_keys(page=page, limit=limit)
    return api_response(
        status_code=200,
        message="Get API keys successfully.",
        details=api_keys
    )
    

# Update an API Key
@router.patch("/api-keys/{key_id}")
async def update_api_key(
    key_id: str,
    update_data: Optional[api_key_schema.APIKeyUpdateSchema] = None
):
    if update_data:
        update_data = jsonable_encoder(update_data)
        update_data = {k: v for k, v in update_data.items() if v is not None}
    else:
        update_data = {}
    
    updated_key = await model_controller.update_api_key(key_id, update_data)
    return api_response(
        status_code=200,
        message="API key updated successfully.",
        details=jsonable_encoder(updated_key)
    )
    
    
# Delete an API Key
@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str):
    await model_controller.delete_api_key(key_id)
    return api_response(
        status_code=200,
        message="API key deleted successfully."
    )

# Toggle API Key Usage Status
@router.patch("/api-keys/{key_id}/toggle-status")
async def toggle_api_key_status(
    key_id: str,
    toggle_data: Optional[api_key_schema.APIKeyUsageToggleSchema] = None
):
    if toggle_data:
        toggle_data = jsonable_encoder(toggle_data)
        using_model = toggle_data.get("using_model")
    else:
        using_model = None
    
    updated_key = await model_controller.toggle_api_key_status(key_id, using_model)
    return api_response(
        status_code=200,
        message="API key status toggled successfully.",
        details=jsonable_encoder(updated_key)
    )
    
    
# Get all available models
@router.post("/available-models")
async def get_available_models(
    request: api_key_schema.GetAvailableModelsSchema
):
    request = jsonable_encoder(request)
    models = await model_controller.get_available_models(request)
    return api_response(
        status_code=200,
        message="Get available models successfully.",
        details={"models": models}
    )