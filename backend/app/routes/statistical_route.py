from typing import Optional
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
async def get_popular_questions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_display: bool = Query(True),
    faculty: Optional[str] = None, #Admin
    current_user=Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    result = await statistical_controller.get_popular_questions(page, limit, is_display, faculty, current_user)
    return api_response(
        status_code=200,
        message="Get popular questions statistics records successfully.",
        details=result   
    )
    

# Toggle popular question display status
@router.patch("/popular-questions/{question_id}/toggle-display")
async def toggle_popular_question_display(
    question_id: str,
    current_user=Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    result = await statistical_controller.toggle_popular_question_display(question_id, current_user)
    return api_response(
        status_code=200,
        message="Update popular question status successfully.",
        details=result   
    )


# Assign faculty scope to popular question (Admin only)
@router.patch("/popular-questions/{question_id}/assign-faculty")
async def assign_faculty_scope_to_popular_question(
    question_id: str,
    faculty: Optional[statistical_schema.AssignFacultyScopeRequestSchema] = None,
    require_admin = Depends(auth_service.require_role([Role.ADMIN.value]))
):
    faculty = None if faculty is None else jsonable_encoder(faculty)["faculty"]
    result = await statistical_controller.assign_faculty_scope_to_popular_question(question_id, faculty)
    return api_response(
        status_code=200,
        message="Assign faculty scope to popular question successfully.",
        details=result   
    )


# Update popular question (Question / Answer)
@router.patch("/popular-questions/{question_id}/update")
async def update_popular_question(
    question_id: str,
    update_data: statistical_schema.UpdatePopularQuestionRequestSchema,
    current_user=Depends(auth_service.get_current_user)
):
    update_data = jsonable_encoder(update_data)
    current_user = jsonable_encoder(current_user)
    result = await statistical_controller.update_popular_question(question_id, update_data, current_user)
    return api_response(
        status_code=200,
        message="Update popular question successfully.",
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