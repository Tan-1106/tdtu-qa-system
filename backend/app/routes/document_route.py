from fastapi import APIRouter, UploadFile
from app.utils.api_response import api_response
from app.controllers import document_controller

router = APIRouter(prefix="/documents", tags=["Documents"])

# CRUD Endpoints
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
        if doc:
            return api_response(
                status_code=200,
                message="Document retrieved successfully.",
                details=doc,
            )
        else:
            return api_response(status_code=404, message="Document not found.")
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )

# Create a new document
@router.post("/")
async def create_document(doc: dict):
    try:
        created_doc = await document_controller.create_document(doc)
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
async def update_document(doc_id: str, doc_update: dict):
    try:
        updated_doc = await document_controller.update_document(doc_id, doc_update)
        if updated_doc:
            return api_response(
                status_code=200,
                message="Document updated successfully.",
                details=updated_doc,
            )
        else:
            return api_response(status_code=404, message="Document not found.")
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )
    
# Delete a document by ID
@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    try:
        deleted = await document_controller.delete_document(doc_id)
        if deleted:
            return api_response(
                status_code=200,
                message="Document deleted successfully.",
                details=None,
            )
        else:
            return api_response(message="Document not found.", status_code=404)
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
        )

# API Endpoints
# Upload a document
# @router.post("/upload")
# async def upload_document(
#     file: UploadFile,
#     title: str = Form(...),
#     doc_type: str = Form(""),
#     tags: Optional[str] = Form(None),
#     language: Optional[str] = Form('["vi"]'),
#     file_url: str = Form(...),
# ):
#     try:
#         # Extract text and tables from the PDF
#         file_content = await extract_pdf_document_content(file)
        
#         # Upload document
#         result = await process_document(
#             file_content=file_content,
#             title=title,
#             doc_type=doc_type,
#             tags=tags,
#             language=language,
#             file_url=file_url
#         )
        
#         return api_response(
#             status_code=200,
#             message="Document uploaded and processed successfully.",
#             details=result,
#         )
        
#     except Exception as e:
#         return api_response(status_code=500, message=str(e))

# API Endpoints
# Upload a document