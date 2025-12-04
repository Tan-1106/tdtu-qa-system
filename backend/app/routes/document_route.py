# --- ROUTERS ---
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form, Query

from app.services import auth_service
from app.utils.basic_information import Role
from app.utils.api_response import api_response
from app.controllers import document_controller


# --- ROUTERS ---
admin_router = APIRouter(
    prefix="/document",
    tags=["Document"],
    dependencies=[
        Depends(auth_service.require_role([Role.ADMIN.value]))
    ]
)


# --- ADMIN ROUTES ---
# Upload a new document
@admin_router.post("/upload")
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
        details=None
    )