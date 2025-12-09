from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Query

from app.services import auth_service
from app.schemas import statistical_schema
from app.utils.basic_information import Role
from app.utils.api_response import api_response
from app.controllers import statistical_controller


# --- ROUTER ---
router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
    dependencies=[
        Depends(auth_service.get_current_user)
    ]
)


# --- ADMIN ROUTES ---
# Common question statistics
@router.get("/generate-popular-questions")
async def popular_questions_statistics(
    period_type: statistical_schema.PeriodType = Query(...),
    n: int = Query(10),
    current_user=Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    result = await statistical_controller.popular_questions_statistics(period_type, n, current_user)
    return api_response(
        status_code=200,
        message="Get popular questions successfully.",
        details=result   
    )
    

# Get popular questions statistics records
@router.get("/popular-questions")
async def get_popular_questions():
    result = await statistical_controller.get_popular_questions()
    return api_response(
        status_code=200,
        message="Get popular questions statistics records successfully.",
        details=result   
    )
    
    
# Get question statistics
@router.get("/questions-statistics")
async def get_total_questions(
    period_type: statistical_schema.PeriodType = Query(...),
    require_admin = Depends(auth_service.require_role([Role.ADMIN.value]))
):
    result = await statistical_controller.questions_statistics(period_type)
    return api_response(
        status_code=200,
        message="Get total questions successfully.",
        details=result
    )