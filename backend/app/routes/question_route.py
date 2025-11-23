from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import question_schema
from app.controllers import question_controller
from app.utils.api_response import api_response


# --- ROUTERS ---
admin_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)


user_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# --- ADMIN ROUTES ---
# Lấy tất cả câu hỏi
@admin_router.get("/")
async def get_questions():
    try:
        questions = await question_controller.get_questions()
        return api_response(
            status_code=200,
            message="Lấy tất cả câu hỏi thành công.",
            details=questions
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
       
        
# Lấy câu hỏi theo ID
@admin_router.get("/{question_id}")
async def get_question(question_id: str):
    try:
        question = await question_controller.get_question_by_id(question_id)
        return api_response(
            status_code=200,
            message="Lấy câu hỏi thành công.",
            details=question
        )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy câu hỏi.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        

# Xem danh sách lịch sử hỏi-đáp của người dùng theo user ID (Tối đa 30 bản ghi gần nhất)
# TODO


# Thống kê số lượng câu hỏi theo ngày/tháng/năm
# TODO


# Thống kê phản hồi người dùng theo Like/Dislike
# TODO


# Xem chi tiết câu hỏi và trả lời theo question ID
# TODO
       
       
# --- USER ROUTES ---
# Đặt câu hỏi
@user_router.post("/query")
async def query(
    question: question_schema.QuestionCreate,
    current_user = Depends(auth_service.get_current_user)
):
    try:
        question = jsonable_encoder(question)
        current_user = jsonable_encoder(current_user)
        created_question = await question_controller.query(question, current_user["_id"])
        return api_response(
            status_code=201,
            message="Đặt câu hỏi thành công.",
            details=created_question
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Yêu cầu không hợp lệ.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
      
        
# Để lại phản hồi cho câu trả lời
@user_router.post("/{question_id}/feedback")
async def leave_feedback(
    question_id: str,
    feedback: question_schema.LeaveFeedback,
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)
        feedback = jsonable_encoder(feedback)
        updated_question = await question_controller.leave_feedback(
            question_id=question_id,
            user_id=current_user["_id"],
            feedback=feedback["feedback"]
        )
        return api_response(
            status_code=200,
            message="Để lại phản hồi thành công.",
            details=updated_question,
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Yêu cầu không hợp lệ.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
    
# Xem danh sách lịch sử hỏi-đáp của người dùng hiện tại (Tối đa 30 bản ghi gần nhất)
# TODO