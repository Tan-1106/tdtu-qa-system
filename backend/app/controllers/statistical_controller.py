from app.utils.basic_information import Role
from app.utils.api_response import UserError
from app.services import statistical_service, user_service


# Common question statistics
async def popular_questions_statistics(
    period_type: str,
    n: int,
    current_user: dict
):
    if current_user["role"] != Role.ADMIN.value:
        raise UserError("You do not have permission to access this resource.")
    
    result = await statistical_service.popular_questions_statistics(period_type, n)
    return result


# Get popular questions statistics records
async def get_popular_questions(page: int, limit: int, is_display: bool, faculty: str, current_user: dict):
    if faculty and current_user["role"] != Role.ADMIN.value:
        raise UserError("You do not have permission to access this resource.")
    
    if current_user["role"] != Role.ADMIN.value:
        faculty = current_user["faculty"]
    
    if current_user["role"] != Role.ADMIN.value and not current_user["is_faculty_manager"]:
        is_display = True
        
    result = await statistical_service.get_popular_questions(page, limit, is_display, faculty)
    return result


# Get popular question statistics for student
async def get_popular_questions_student(page: int, limit: int, faculty_only: bool, current_user: dict):
    faculty = current_user["faculty"]
    result = await statistical_service.get_popular_questions_student(page, limit, faculty, faculty_only)
    return result


# Toggle popular question display status
async def toggle_popular_question_display(
    question_id: str,
    current_user: dict
):
    if current_user["role"] != Role.ADMIN.value and not current_user["is_faculty_manager"]:
        raise UserError("You do not have permission to access this resource.")
    
    question = await statistical_service.get_popular_question_by_id(question_id)
    if current_user["is_faculty_manager"] and question["summary"]["faculty_scope"] != current_user["faculty"]:
        raise UserError("You do not have permission to update this question.")
        
    result = await statistical_service.toggle_popular_question_display(question_id)
    return result


# Assign faculty scope to popular question
async def assign_faculty_scope_to_popular_question(question_id: str, faculty: str):
    faculties = await user_service.get_all_existing_faculties()
    if faculty not in faculties and faculty is not None:
        raise UserError("Invalid faculty specified.")
    
    result = await statistical_service.assign_faculty_scope_to_popular_question(question_id, faculty)
    return result


# Update popular question
async def update_popular_question(question_id: str, update_data: dict, current_user: dict):
    question = await statistical_service.get_popular_question_by_id(question_id)
    
    if current_user["role"] != Role.ADMIN.value and not current_user["is_faculty_manager"]:
        raise UserError("You do not have permission to access this resource.")
    
    if current_user["is_faculty_manager"] and question["summary"]["faculty_scope"] != current_user["faculty"]:
        raise UserError("You do not have permission to update this question.")
    
    update_data = { k: v for k, v in update_data.items() if v is not None and v != "" }
    
    result = await statistical_service.update_popular_question(question_id, update_data)
    return result


# Get total questions
async def questions_statistics(period_type: str):
    result = await statistical_service.questions_statistics(period_type)
    return result