from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form

from app.services import auth_service
from app.schemas import document_schema
from app.controllers import document_controller
from app.utils.api_response import api_response

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)

# Get all documents
@router.get("/")
async def get_documents():
    try:
        docs = await document_controller.get_documents()
        return api_response(
            status_code=200,
            message="Documents retrieved successfully.",
            details=docs
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        ) 
        
# Get a document by ID
@router.get("/{doc_id}")
async def get_document(doc_id: str):
    try:
        doc = await document_controller.get_document_by_id(doc_id)
        return api_response(
                status_code=200,
                message="Document retrieved successfully.",
                details=doc,
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )

# Create a new document
@router.post("/")
async def create_document(doc: document_schema.DocumentCreate, current_user = Depends(auth_service.get_current_user)):
    try:
        current_user = jsonable_encoder(current_user)
        uploaded_by = current_user["_id"]

        created_doc = await document_controller.create_document(doc, uploaded_by)
        return api_response(
            status_code=201,
            message="Document created successfully.",
            details=created_doc
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )
    
# Update a document by ID
@router.patch("/{doc_id}")
async def update_document(doc_id: str, doc_update: document_schema.DocumentUpdate, current_user = Depends(auth_service.get_current_user)):
    try:
        current_user = jsonable_encoder(current_user)
        edited_by = current_user["_id"]

        updated_doc = await document_controller.update_document(doc_id, doc_update, edited_by)
        return api_response(
                status_code=200,
                message="Document updated successfully.",
                details=updated_doc,
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )
    
# Delete a document by ID
@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    try:
        await document_controller.delete_document(doc_id)
        return api_response(
                status_code=200,
                message="Document deleted successfully.",
                details=None,
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )

# Upload a document
# (PDF -> Extract text -> Chunk text -> Generate questions -> Get embeddings -> Store in DB)
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    title: str = Form(...),
    doc_type: Optional[str] = Form(""),
    tags: Optional[str] = Form(None),
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)
        uploaded_by = current_user["_id"]
        
        result = await document_controller.upload_document(
            file=file,
            title=title,
            doc_type=doc_type,
            tags=tags,
            language=language,
            file_url=file_url,
            uploaded_by=uploaded_by
        )
        return api_response(
            status_code=200,
            message="Document uploaded successfully.",
            details=result
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
        
# Upload appendix document (PDF)
@router.post("/upload-appendix")
async def upload_appendix_document(
    file: UploadFile,
    title: str = Form(...),
    doc_type: Optional[str] = Form(""),
    tags: Optional[str] = Form(None),
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...),
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)
        uploaded_by = current_user["_id"]
        
        result = await document_controller.upload_appendix_document(
            file=file,
            title=title,
            doc_type=doc_type,
            tags=tags,
            language=language,
            file_url=file_url,
            uploaded_by=uploaded_by
        )
        return api_response(
            status_code=200,
            message="Appendix document uploaded successfully.",
            details=result
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )