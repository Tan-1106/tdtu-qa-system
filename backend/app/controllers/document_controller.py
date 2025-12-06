import os
from urllib.parse import urlparse

from fastapi import UploadFile, Form
from app.utils.api_response import UserError, AuthException
from app.services import document_service
from app.utils.basic_information import Faculty, Role
from app.services import llm_service, embedding_service, document_chunk_service


# --- ROUTERS ---
# Upload a new document
async def upload_document(
    file: UploadFile,
    doc_type: str,
    department: str = None,
    faculty: str = None,
    file_url: str = Form(...),
    current_user: dict = None,
):
    if current_user["role"] == Role.STUDENT.value:
        raise AuthException("You do not have permission to upload documents.")
    if current_user["role"] == Role.ADMIN.value:
        if department is None and faculty is None:
            raise UserError("Either department or faculty must be provided.")
        if department is not None and faculty is not None:
            raise UserError("Only one of department or faculty can be provided.")
        if faculty is not None and faculty not in [f.value.name for f in Faculty]:
            raise UserError("Invalid faculty provided.")
    if not all([urlparse(file_url).scheme, urlparse(file_url).netloc]):
        raise UserError("Invalid file URL provided.")
    if file.content_type != "application/pdf":
        raise UserError("Only PDF files are allowed.")
    
    if current_user["role"] == Role.FACULTY_MANAGER.value:
        department = None
        faculty = current_user["faculty"]    
    try:
        # Extract text content from the uploaded PDF file
        document_content = await document_service.extract_file_content(file)
        await file.seek(0)
        
        # Save file to server
        file_path = await document_service.save_document_file(file)
        
        # Create document record in database
        file_name = os.path.splitext(file.filename)[0]
        document_record = {
            "file_name": file_name,
            "doc_type": doc_type,
            "department": department,
            "faculty": faculty,
            "file_url": file_url,
            "uploaded_by": current_user["_id"],
            "file_path": file_path
        }
        new_document = await document_service.store_document_record(document_record)
        
        # Split text into chunks
        chunks = await document_service.split_text_into_chunks(document_content, words_per_chunk=800, overlap=200)
        
        # Generate chunk potential questions
        api_key = await llm_service.get_current_api_key()
        if not api_key:
            raise UserError("No active API key found. Please activate an API key to proceed.")
        
        document_chunks_record = {
            "doc_id": new_document["id"],
            "chunks": {}
        }
        for idx, chunk in enumerate(chunks):
            potential_questions = await llm_service.generate_potential_questions(
                api_key=api_key,
                context=chunk,
                num_questions=2
            )
            document_chunks_record["chunks"][str(idx)] = {
                "text": chunk,
                "potential_questions": potential_questions,
                "embedding_ids": []
            }
                    
        # Convert potential question and store in ChromaDB
        for idx, chunk_data in document_chunks_record["chunks"].items():
            for question in chunk_data["potential_questions"]:
                embedding = await embedding_service.store_embedding(
                    text=question,
                    metadatas={
                        "doc_id": new_document["id"],
                        "chunk_index": int(idx),
                        "faculty": faculty if faculty else ""
                    }
                )
                chunk_data["embedding_ids"].append(embedding["embedding_id"])               
                
        # Store document chunks record in database
        await document_chunk_service.store_document_chunks_record(document_chunks_record)
        return new_document
        
    except Exception as e:
        await document_service.delete_document_file(file_path)
        await document_service.delete_document_record(new_document["id"])        
        await embedding_service.delete_embeddings_by_doc_id(new_document["id"])
        await document_chunk_service.delete_document_chunks_by_doc_id(new_document["id"])
        
        raise Exception("Failed to upload document.")
    

# Get general documents
async def get_general_documents(
    page: int,
    limit: int,
    doc_type: str = None,
    department: str = None,
    keyword: str = None
):
    documents = await document_service.get_general_documents(
        page=page,
        limit=limit,
        doc_type=doc_type,
        department=department,
        keyword=keyword
    )
    return documents


# Get faculty documents
async def get_faculty_documents(
    page: int,
    limit: int,
    doc_type: str = None,
    faculty: str = None,
    keyword: str = None,
    current_user: dict = None
):
    if current_user["role"] != Role.ADMIN.value:
        faculty = current_user["faculty"]
    
    documents = await document_service.get_faculty_documents(
        page=page,
        limit=limit,
        doc_type=doc_type,
        faculty=faculty,
        keyword=keyword
    )
    return documents


# Update document information
async def update_document(
    doc_id: str,
    data: dict,
    current_user: dict = None
):
    document = await document_service.get_document_by_id(doc_id)
    
    if current_user["role"] == Role.ADMIN.value:
        if data["department"] is not None and data["faculty"] is not None:
            raise UserError("Only one of department or faculty can be provided.")
        if data["faculty"] is not None and data["faculty"] not in [f.value.name for f in Faculty]:
            raise UserError("Invalid faculty provided.")
        if data["faculty"] is not None:
            data["department"] = None
        if data["department"] is not None:
            data["faculty"] = None
    
    if current_user["role"] == Role.FACULTY_MANAGER.value:
        if document["faculty"] != current_user["faculty"]:
            raise AuthException("You do not have permission to update this document.")
        if document["department"] is not None:
            raise AuthException("You do not have permission to update department documents.")
        if data["faculty"] is not None or data["department"] is not None:
            raise AuthException("You do not have permission to update faculty or department.")
    
    if current_user["role"] == Role.STUDENT.value:
        raise AuthException("You do not have permission to update documents.")
    
    data["updated_by"] = current_user["_id"]
    data = {
        k: v for k, v in data.items() 
        if v is not None or (k in ['faculty', 'department'] and not (data.get('faculty') is None and data.get('department') is None))
    }
    
    updated_document = await document_service.update_document_record(doc_id, data)
    return updated_document


# Delete a document
async def delete_document(
    doc_id: str,
    current_user: dict = None
):
    document = await document_service.get_document_by_id(doc_id)
    
    if current_user["role"] == Role.FACULTY_MANAGER.value:
        if document["faculty"] != current_user["faculty"]:
            raise AuthException("You do not have permission to delete this document.")
        if document["department"] is not None:
            raise AuthException("You do not have permission to delete department documents.")
    
    if current_user["role"] == Role.STUDENT.value:
        raise AuthException("You do not have permission to delete documents.")
    
    # Delete document file from server
    await document_service.delete_document_file(document["file_path"])
    
    # Delete document record from database
    await document_service.delete_document_record(doc_id)
    
    # Delete document chunks from database
    await document_chunk_service.delete_document_chunks_by_doc_id(doc_id)
    
    # Delete embeddings from ChromaDB
    await embedding_service.delete_embeddings_by_doc_id(doc_id)
    
    return {"message": "Document deleted successfully."}