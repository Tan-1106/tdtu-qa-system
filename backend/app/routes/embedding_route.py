from fastapi import APIRouter, Depends, Query

from app.services import auth_service
from app.utils.basic_information import Role
from app.utils.api_response import api_response
from app.controllers import embedding_controller


# --- ROUTER ---
router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
    dependencies=[
        Depends(auth_service.require_role([Role.ADMIN.value]))
    ]
)


# --- DEV ROUTES ---
# Get embedding vectors
@router.get("/")
async def get_embedding_vectors(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    vectors = await embedding_controller.get_embedding_vectors(page, limit)
    return api_response(
        status_code=200,
        message="Get embedding vectors successfully.",
        details=vectors
    )
    
    
# Reset collection
@router.delete("/reset")
async def reset_embeddings():
    success = await embedding_controller.reset_embeddings()
    return api_response(
        status_code=200,
        message="Reset embeddings successfully.",
        details=success
    )
    
    
# --- ROUTES ---
# Scan document chunk collection and recreate embeddings
@router.post("/recreate")
async def recreate_embeddings():
    success = await embedding_controller.recreate_embeddings()
    return api_response(
        status_code=200,
        message="Recreate embeddings successfully.",
        details=success
    )