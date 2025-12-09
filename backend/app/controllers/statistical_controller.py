from app.utils.basic_information import Role
from app.utils.api_response import UserError
from app.services import statistical_service

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
async def get_popular_questions():
    result = await statistical_service.get_popular_questions()
    return result


# Get total questions
async def questions_statistics(period_type: str):
    result = await statistical_service.questions_statistics(period_type)
    return result