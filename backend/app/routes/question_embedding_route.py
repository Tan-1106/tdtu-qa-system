from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile

from app.services import auth_service
from app.utils.api_response import api_response
from app.schemas import question_embedding_schema
from app.controllers import question_embedding_controller


# --- ROUTER ---
router = APIRouter(
    prefix="/question-embeddings",
    tags=["Question Embeddings"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)


# --- ROUTES ---
# Lấy tất cả embeddings câu hỏi tiềm năng
@router.get("/")
async def get_question_embeddings():
    try:
        embeddings = await question_embedding_controller.get_question_embeddings()
        return api_response(
            status_code=200,
            details=embeddings,
            message="Lấy tất cả embeddings câu hỏi tiềm năng thành công."
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi khi lấy embeddings câu hỏi tiềm năng.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
        
# Xuất embeddings câu hỏi tiềm năng ra file JSON
@router.get("/export")
async def export_question_embeddings():
    try:
        embeddings = await question_embedding_controller.get_question_embeddings()
        data = jsonable_encoder(embeddings)
        filename = f"question_embeddings_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        return JSONResponse(
            content=data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Cache-Control": "no-store"
            }
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
       
        
# Nhập embeddings câu hỏi tiềm năng từ file JSON
@router.post("/import")
async def import_question_embeddings(file: UploadFile):
    try:
        result = await question_embedding_controller.import_question_embeddings_file(file=file)
        return api_response(
            status_code=200,
            message="Nhập embeddings câu hỏi tiềm năng thành công.",
            details=result
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Dữ liệu không hợp lệ.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )


# Lấy embedding câu hỏi theo ID
@router.get("/{embedding_id}")
async def get_question_embedding(embedding_id: str):
    try:
        embedding = await question_embedding_controller.get_question_embedding_by_id(embedding_id)
        return api_response(
                status_code=200,
                details=embedding,
                message="Lấy embedding câu hỏi thành công."
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy embedding câu hỏi.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )


# Tạo embedding câu hỏi mới
@router.post("/")
async def create_question_embedding(data: question_embedding_schema.QuestionEmbeddingCreate):
    try:
        data = jsonable_encoder(data)
        created_question_embedding = await question_embedding_controller.create_question_embedding(data)
        return api_response(
            status_code=201,
            message="Tạo embedding câu hỏi thành công.",
            details=created_question_embedding
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Dữ liệu không hợp lệ.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
    
    
# Xóa embedding câu hỏi theo ID
@router.delete("/{embedding_id}")
async def delete_question_embedding(embedding_id: str):
    try:
        await question_embedding_controller.delete_question_embedding(embedding_id)
        return api_response(
            status_code=200,
            message="Xóa embedding câu hỏi thành công.",
            details=None
        )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy embedding câu hỏi.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
    
    
# Đặt lại (Xóa) toàn bộ embeddings câu hỏi
@router.delete("/")
async def reset_question_embeddings_collection():
    try:
        await question_embedding_controller.reset_question_embeddings_collection()
        return api_response(
            status_code=200,
            message="Đặt lại toàn bộ embeddings câu hỏi thành công.",
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        