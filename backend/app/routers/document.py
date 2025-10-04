from fastapi import Form
from typing import Optional
from fastapi import APIRouter, UploadFile
from fastapi.encoders import jsonable_encoder
from app.utils.api_response import success_response, error_response

from app.database.crud import document
from app.services.document import extract_pdf_document_content, upload_document
from app.schemas.document import DocumentCreate, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["Documents"])

# Các routes này chỉ gọi để test crud, không phải api thành phẩm thật sự
# Get all documents
# @router.get("/")
# async def get_documents():
#     try:
#         docs = await document.get_documents()
#         return success_response(
#             message="Documents retrieved successfully.",
#             status_code=200,
#             data=docs
#         )
#     except Exception as e:
#         return error_response(
#             message=str(e),
#             status_code=500
#         ) 

# # Get a document by ID
# @router.get("/{doc_id}")
# async def get_document(doc_id: str):
#     try:
#         doc = await document.get_document_by_id(doc_id)
#         if doc:
#             return success_response(
#                 data=doc,
#                 message="Document retrieved successfully.",
#                 status_code=200
#             )
#         else:
#             return error_response(message="Document not found.", status_code=404)
#     except Exception as e:
#         return error_response(message=str(e))

# # Create a new document
# @router.post("/")
# async def create_document(doc: DocumentCreate):
#     try:
#         doc = jsonable_encoder(doc)
#         created_doc = await document.create_document(doc)
#         return success_response(
#             data=created_doc,
#             message="Document created successfully.",
#             status_code=201
#         )
#     except Exception as e:
#         return error_response(message=str(e))
    
# # Update a document by ID
# @router.patch("/{doc_id}")
# async def update_document(doc_id: str, doc_update: DocumentUpdate):
#     try:
#         update_data = doc_update.model_dump(exclude_none=True)
#         update_data = jsonable_encoder(update_data)

#         if len(update_data) == 1 and "edited_by" in update_data:
#             return error_response(message="No fields to update.", status_code=400)

#         updated_doc = await document.update_document(doc_id, update_data)
#         if updated_doc:
#             return success_response(
#                 data=updated_doc,
#                 message="Document updated successfully.",
#                 status_code=200
#             )
#         else:
#             return error_response(message="Document not found.", status_code=404)
#     except Exception as e:
#         return error_response(message=str(e))
    
# # Delete a document by ID
# @router.delete("/{doc_id}")
# async def delete_document(doc_id: str):
#     try:
#         deleted = await document.delete_document(doc_id)
#         if deleted:
#             return success_response(
#                 data=None,
#                 message="Document deleted successfully.",
#                 status_code=200
#             )
#         else:
#             return error_response(message="Document not found.", status_code=404)
#     except Exception as e:
#         return error_response(message=str(e))

# Upload a document
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    title: str = Form(...),
    doc_type: str = Form(""),
    tags: Optional[str] = Form(None),
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...),
):
    try:
        # Extract text and tables from the PDF
        file_content = await extract_pdf_document_content(file)
        
        # Upload document
        result = await upload_document(
            file_content=file_content["text"],
            title=title,
            doc_type=doc_type,
            tags=tags,
            language=language,
            file_url=file_url
        )
        
        return success_response(
            data=result,
            message="Document uploaded and processed successfully.",
            status_code=200
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)
    
# Upload an appendix (must be text-based PDF) (LATER)
# @router.post("/upload-appendix")
# async def upload_appendix(file: UploadFile):
#     pass