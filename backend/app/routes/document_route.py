# --- ROUTERS ---
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form, Query

from app.services import auth_service
from app.utils.basic_information import Role
from app.utils.api_response import api_response
from app.controllers import document_controller
from app.schemas import document_schema


# --- ROUTERS ---
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[
        Depends(auth_service.require_role([Role.ADMIN.value, Role.FACULTY_MANAGER.value]))
    ]
)


# --- ADMIN ROUTES ---
# Upload a new document
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    doc_type: str = Form(...),
    department: str = Form(None),
    faculty: str = Form(None),
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    uploaded_document = await document_controller.upload_document(
        file=file,
        doc_type=doc_type,
        department=department,
        faculty=faculty,
        file_url=file_url,
        uploaded_by=current_user["_id"]
    )
    return api_response(
        status_code=201,
        message="Document uploaded successfully.",
        details=uploaded_document
    )
    
    
# Get documents (with pagination)
@router.get("/")
async def get_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    doc_type: str = Query(None),
    department: str = Query(None),
    faculty: str = Query(None),
    keyword: str = Query(None)
):
    documents = await document_controller.get_documents(page, limit, doc_type, department, faculty, keyword)
    return api_response(
        status_code=200,
        message="Get documents list successfully.",
        details=documents
    )
    
    
# Update document information
@router.patch("/{doc_id}")
async def update_document(
    doc_id: str,
    data: document_schema.DocumentUpdateSchema
):
    data = jsonable_encoder(data)
    updated_document = await document_controller.update_document(doc_id, data)
    return api_response(
        status_code=200,
        message="Document information updated successfully.",
        details=updated_document
    )