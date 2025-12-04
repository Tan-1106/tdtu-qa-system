import os
from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile, Form
from app.utils.api_response import UserError
from app.services import document_service, model_service


# --- ROUTERS ---
# Upload a new document
async def upload_document(
    file: UploadFile,
    doc_type: str,
    department: Optional[str] = None,
    faculty: Optional[str] = None,
    file_url: str = Form(...),
    uploaded_by: str = Form(...)
):
    print("- Document type: ", doc_type, " - Type:", type(doc_type))
    print("- Department: ", department, " - Type:", type(department))
    print("- Faculty: ", faculty, " - Type:", type(faculty))
    print("- File URL: ", file_url, " - Type:", type(file_url))
    print("- Uploaded by: ", uploaded_by, " - Type:", type(uploaded_by))
    if department is None and faculty is None:
        raise UserError("Either department or faculty must be provided.")
    if department is not None and faculty is not None:
        raise UserError("Only one of department or faculty can be provided.")
    if not all([urlparse(file_url).scheme, urlparse(file_url).netloc]):
        raise UserError("Invalid file URL provided.")
    if file.content_type != "application/pdf":
        raise UserError("Only PDF files are allowed.")
    
    # Create document record
    file_name = os.path.splitext(file.filename)[0]
    document_record = {
        "filename": file_name,
        "doc_type": doc_type,
        "department": department,
        "faculty": faculty,
        "file_url": file_url,
        "uploaded_by": uploaded_by
    }
    

    # Extract text content from the uploaded PDF file
    document_content = await document_service.extract_file_content(file)
    await file.seek(0)
    
    # Split text into chunks
    chunks = await document_service.split_text_into_chunks(document_content, words_per_chunk=800, overlap=200)
    
    # Generate chunk potential questions
    api_key = await model_service.get_current_api_key()
    if not api_key:
        raise UserError("No active API key found. Please activate an API key to proceed.")
    
    # Create document chunks record
    document_chunks_record = {
        "doc_id": None,
        "chunks": {}
    }
    for idx, chunk in enumerate(chunks):
        potential_questions = model_service.generate_potential_questions(
            api_key=api_key,
            context=chunk,
            num_questions=5
        )
        document_chunks_record["chunks"][str(idx)] = {
            "text": chunk,
            "potential_questions": potential_questions
        }
    
    