from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import prototype_schema
from app.utils.api_response import api_response
from app.controllers import prototype_controller

router = APIRouter(
    prefix="/prototypes",
    tags=["Prototypes"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)


# Get all prototypes
@router.get("/")
async def get_prototypes():
    try:
        prototypes = await prototype_controller.get_prototypes()
        return api_response(
            status_code=200,
            details=prototypes,
            message="Prototypes retrieved successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )


# Get a prototype by ID
@router.get("/{prototype_id}")
async def get_prototype(prototype_id: str):
    try:
        prototype = await prototype_controller.get_prototype_by_id(prototype_id)
        return api_response(
            status_code=200,
            details=prototype,
            message="Prototype retrieved successfully."
        )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )


# Create a prototype (JUST FOR TESTING)
@router.post("/")
async def create_prototype(data: prototype_schema.PrototypeCreate):
    try:
        data = jsonable_encoder(data)
        created_prototype = await prototype_controller.create_prototype(data)
        return api_response(
            status_code=200,
            details=created_prototype,
            message="Prototype created successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
      
        
# Cluster question embeddings into prototypes
@router.post("/cluster")
async def cluster_question_embeddings():
    try:
        await prototype_controller.cluster_question_embeddings()
        return api_response(
            status_code=200,
            message="Question embeddings clustered into prototypes successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )


# Reset (delete) prototypes collection
@router.delete("/")
async def reset_prototypes_collection():
    try:
        await prototype_controller.reset_prototypes_collection()
        return api_response(
            status_code=200,
            message="Prototypes collection reset successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )