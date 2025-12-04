import os
from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile, Form
from app.utils.api_response import UserError
from app.services import document_service
from app.services import llm_service, embedding_service, document_chunk_service


# --- ROUTERS ---
# Upload a new document
async def upload_document(
    uploaded_by: str,
    file: UploadFile,
    doc_type: str,
    department: Optional[str] = None,
    faculty: Optional[str] = None,
    file_url: str = Form(...)
):
    if department is None and faculty is None:
        raise UserError("Either department or faculty must be provided.")
    if department is not None and faculty is not None:
        raise UserError("Only one of department or faculty can be provided.")
    if not all([urlparse(file_url).scheme, urlparse(file_url).netloc]):
        raise UserError("Invalid file URL provided.")
    if file.content_type != "application/pdf":
        raise UserError("Only PDF files are allowed.")
    
    try:
        # Extract text content from the uploaded PDF file
        document_content = await document_service.extract_file_content(file)
        await file.seek(0)
        
        # Save file to server
        file_path = await document_service.save_document_file(file)
        
        # Create document record in database
        file_name = os.path.splitext(file.filename)[0]
        document_record = {
            "filename": file_name,
            "doc_type": doc_type,
            "department": department,
            "faculty": faculty,
            "file_url": file_url,
            "uploaded_by": uploaded_by,
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
            potential_questions = llm_service.generate_potential_questions(
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
                        "faculty": faculty if faculty else "",
                        "department": department if department else ""
                    }
                )
                chunk_data["embedding_ids"].append(embedding["embedding_id"])               
                
        # Store document chunks record in database
        await document_chunk_service.store_document_chunks_record(document_chunks_record)
        
    except Exception as e:
        await document_service.delete_document_file(file_path)
        await document_service.delete_document_record(new_document["id"])        
        await embedding_service.delete_embeddings_by_doc_id(new_document["id"])
        await document_chunk_service.delete_document_chunks_by_doc_id(new_document["id"])
        
        raise Exception("Failed to upload document.")
    