from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form, Query

from app.services import auth_service
from app.schemas import document_schema
from app.controllers import document_controller
from app.utils.api_response import api_response


# --- ROUTERS ---
admin_route = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)


user_route = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# --- ADMIN ROUTES ---
# Lấy chunk tài liệu theo document ID và chunk index
@admin_route.get("/{doc_id}/chunks/{chunk_index}")
async def get_chunk(
    doc_id: str, 
    chunk_index: int
):
    try:
        chunk = await document_controller.get_document_chunk(doc_id, chunk_index)
        return api_response(
                status_code=200,
                message="Lấy chunk tài liệu thành công.",
                details=chunk
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy chunk tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
    
    
# Cập nhật tài liệu theo ID
@admin_route.patch("/{doc_id}")
async def update_document(
    doc_id: str,
    doc_update: document_schema.DocumentUpdate,
    current_user = Depends(auth_service.get_current_user)
):
    try:
        doc_update = jsonable_encoder(doc_update)
        current_user = jsonable_encoder(current_user)

        updated_doc = await document_controller.update_document(doc_id, doc_update, current_user["_id"])
        return api_response(
                status_code=200,
                message="Cập nhật tài liệu thành công.",
                details=updated_doc
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
   
    
# Xóa tài liệu theo ID
@admin_route.delete("/{doc_id}")
async def delete_document(doc_id: str):
    try:
        await document_controller.delete_document(doc_id)
        return api_response(
                status_code=200,
                message="Xóa tài liệu thành công.",
                details=None,
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )


# Tải tài liệu
@admin_route.post("/upload")
async def upload_document(
    file: UploadFile,
    doc_type: str = Form(...),
    department: str = Form(...),
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)
        result = await document_controller.upload_document(
            file=file,
            doc_type=doc_type,
            department=department,
            language=language,
            file_url=file_url,
            uploaded_by=current_user["_id"]
        )
        return api_response(
            status_code=200,
            message="Tải tài liệu thành công.",
            details=result
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi tải tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
        
# Tải tài liệu phụ lục (PDF)
@admin_route.post("/upload-appendix")
async def upload_appendix_document(
    file: UploadFile,
    doc_type: Optional[str] = Form(...),
    department: str = Form(...),
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)        
        result = await document_controller.upload_appendix_document(
            file=file,
            doc_type=doc_type,
            department=department,
            language=language,
            file_url=file_url,
            uploaded_by=current_user["_id"]
        )
        return api_response(
            status_code=200,
            message="Tải tài liệu phụ lục thành công.",
            details=result
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi tải tài liệu phụ lục.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
        
# --- USER ROUTES ---
# Lấy tất cả tài liệu
@user_route.get("/")
async def get_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: str | None = Query(None),
    department: str | None = Query(None)
):
    try:
        skip = (page - 1) * limit
        filters = {}
        if type:
            filters["doc_type"] = type
        if department:
            filters["department"] = department
        
        total = await document_controller.count_documents(filters=filters)
        total_pages = (total + limit - 1) // limit
        
        docs = await document_controller.get_documents(filters=filters, skip=skip, limit=limit)
        return api_response(
            status_code=200,
            message="Lấy tài liệu thành công.",
            details= {
                "documents": docs,
                "page": page,
                "total_pages": total_pages
            }
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ",
            details=str(e)
        ) 
        
        
# Tìm kiếm tài liệu bằng từ khóa
# TODO



# Xem file tài liệu
@user_route.get("/view/{doc_id}")
async def view_document_file(doc_id: str):
    try:
        file_content = await document_controller.view_document_file(doc_id)
        return file_content
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
        
# Lấy tài liệu theo ID
@user_route.get("/{doc_id}")
async def get_document(doc_id: str):
    try:
        doc = await document_controller.get_document_by_id(doc_id)
        return api_response(
                status_code=200,
                message="Lấy tài liệu thành công.",
                details=doc,
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message="Không tìm thấy tài liệu.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )