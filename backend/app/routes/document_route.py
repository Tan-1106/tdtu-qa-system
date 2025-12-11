from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form, Query

from app.services import auth_service
from app.schemas import document_schema
from app.utils.basic_information import Role
from app.utils.api_response import api_response
from app.controllers import document_controller


# --- ROUTER ---
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[
        Depends(auth_service.get_current_user)
    ]
)


# --- ADMIN ROUTES ---
# Upload a new document
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    doc_type: str = Form(...),
    department: str = Form(None),                           # For Admin only
    faculty: str = Form(None),                              # For Admin only                           
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
        current_user=current_user
    )
    return api_response(
        status_code=201,
        message="Document uploaded successfully.",
        details=uploaded_document
    )
    
    
# Upload appendix document
@router.post("/upload-appendix")
async def upload_appendix_document(
    file: UploadFile,
    doc_type: str = Form(...),
    department: str = Form(None),                           # For Admin only
    faculty: str = Form(None),                              # For Admin only                           
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    uploaded_document = await document_controller.upload_appendix_document(
        file=file,
        doc_type=doc_type,
        department=department,
        faculty=faculty,
        file_url=file_url,
        current_user=current_user
    )
    return api_response(
        status_code=201,
        message="Document uploaded successfully.",
        details=uploaded_document
    )
    
# Get general documents
@router.get("/general")
async def get_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    doc_type: str = Query(None),
    department: str = Query(None),
    keyword: str = Query(None)
):
    documents = await document_controller.get_general_documents(page, limit, doc_type, department, keyword)
    return api_response(
        status_code=200,
        message="Documents retrieved successfully.",
        details=documents
    )
    
    
# Get faculty documents
@router.get("/faculty")
async def get_faculty_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    doc_type: str = Query(None),
    faculty: str = Query(None),                                  # For Admin only
    keyword: str = Query(None),
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    documents = await document_controller.get_faculty_documents(page, limit, doc_type, faculty, keyword, current_user)
    return api_response(
        status_code=200,
        message="Documents retrieved successfully.",
        details=documents
    )
    
    
# Get all existing departments
@router.get("/departments")
async def get_all_departments():
    departments = await document_controller.get_all_departments()
    return api_response(
        status_code=200,
        message="Departments retrieved successfully.",
        details=departments
    )
    
    
# Get all existing doc types
@router.get("/doc-types")
async def get_all_doc_types():
    doc_types = await document_controller.get_all_doc_types()
    return api_response(
        status_code=200,
        message="Document types retrieved successfully.",
        details=doc_types
    )
    
    
# View document
@router.get("/view/{doc_id}")
async def view_document(
    doc_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    file_content = await document_controller.view_document_file(doc_id, current_user)
    return file_content
    
    
# Update document information
@router.patch("/{doc_id}")
async def update_document(
    doc_id: str,
    data: document_schema.DocumentUpdateSchema,
    current_user = Depends(auth_service.get_current_user)
):
    data = jsonable_encoder(data)
    current_user = jsonable_encoder(current_user)
    updated_document = await document_controller.update_document(doc_id, data, current_user)
    return api_response(
        status_code=200,
        message="Document information updated successfully.",
        details=updated_document
    )
    
    
# Delete a document
@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    await document_controller.delete_document(doc_id, current_user)
    return api_response(
        status_code=200,
        message="Document deleted successfully.", 
        details=None
    )