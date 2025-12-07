from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.schemas import qa_schema
from app.services import auth_service
from app.controllers import qa_controller
from app.utils.api_response import api_response


# --- ROUTER ---
router = APIRouter(
    prefix="/qa",
    tags=["Q&A"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# --- ROUTES ---
@router.post("/qa")
async def qa(
    data: qa_schema.QuestionSchema,
    current_user = Depends(auth_service.get_current_user)
):
    data = jsonable_encoder(data)
    current_user = jsonable_encoder(current_user)
    answer = await qa_controller.get_answer(data["question"], current_user)
    return api_response(
        status_code=200,
        message="Get answer successfully.",
        details=answer
)