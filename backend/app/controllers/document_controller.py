from typing import Optional
from fastapi import UploadFile, Form
from fastapi.encoders import jsonable_encoder

from app.utils import text_process
from app.schemas import document_schema
from app.services import document_service

# Get all documents
async def get_documents():
    docs = await document_service.get_documents()
    return docs

# Get a document by ID
async def get_document_by_id(doc_id: str):
    doc = await document_service.get_document_by_id(doc_id)
    return doc

# Get a document chunk by doc_id and chunk_index
async def get_document_chunk(doc_id: str, chunk_index: int):
    chunk = await document_service.get_document_chunk(doc_id, chunk_index)
    return chunk

# Create a new document
async def create_document(doc_data: document_schema.DocumentCreate, uploaded_by: str):
    doc_data = jsonable_encoder(doc_data)
    doc_data["uploaded_by"] = uploaded_by
    
    doc = await document_service.create_document(doc_data)
    return doc

# Update an existing document
async def update_document(doc_id: str, doc_update: document_schema.DocumentUpdate, edited_by: str):
    update_data = jsonable_encoder(doc_update)
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        raise ValueError("No fields to update.")
    
    update_data["edited_by"] = edited_by
    response = await document_service.update_document(doc_id, update_data)
    return response

# Delete a document by ID
async def delete_document(doc_id: str):
    result = await document_service.delete_document(doc_id)
    return result

# Upload a document
async def upload_document(
    file: UploadFile,
    title: str,
    doc_type: str,
    uploaded_by: str,
    tags: Optional[str] = None,
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...)
):
    # Extract text from PDF
    print("LOG: Extracting text from PDF...")
    document_content = await document_service.extract_pdf_document_content(file)
    
    # Split text into chunks
    print("LOG: Splitting text into chunks...")
    chunks = await text_process.split_text_into_chunks(document_content, words_per_chunk=400, overlap=150)
    
    # Create document record in DB
    print("LOG: Creating document record in DB...")
    doc = await document_service.create_document({
        "title": title,
        "chunks": chunks,
        "doc_type": doc_type,
        "tags": eval(tags) if tags else [],
        "language": eval(language) if language else [],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
    })

    # Prepare response and process document (generate questions, get embeddings, store embeddings in ChromaDB)
    response = {
        "doc_id": str(doc.id),
        "title": title[:20] + "...",
        "num_chunks": len(chunks),
        "doc_type": doc_type,
        "tags": eval(tags) if tags else [],
        "language": eval(language) if language else ["vi"],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
        "questions": []
    }
    
    # Generate questions
    for idx, chunk in enumerate(chunks):
        print("LOG: Generating questions for chunk", idx + 1, "/", len(chunks), "...")
        questions_data = await document_service.create_question_embeddings(str(doc.id), idx, chunk, num_questions=5)
        response["questions"].append(questions_data)
        
    return response

# Upload appendix document
async def upload_appendix_document(
    file: UploadFile,
    title: str,
    doc_type: str,
    uploaded_by: str,
    tags: Optional[str] = None,
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...)
):
    # Extract text and tables from PDF
    print("LOG: Extracting text and tables from PDF appendix...")
    file_content = await document_service.extract_pdf_appendix_content(file)

    # Split appendix into chunks
    print("LOG: Splitting appendix into chunks...")
    appendix_description = file_content["description"]
    tables = file_content["tables"]
    chunks = await document_service.split_appendix_into_chunks(appendix_description, tables, table_header_rows=2)
    
    # Create document record in DB
    print("LOG: Creating document record in DB...")
    doc = await document_service.create_document({
        "title": title,
        "chunks": chunks,
        "doc_type": doc_type,
        "tags": eval(tags) if tags else [],
        "language": eval(language) if language else [],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
    })

    # Prepare response and process document (generate questions, get embeddings, store embeddings in ChromaDB)
    response = {
        "doc_id": str(doc.id),
        "title": title[:20] + "...",
        "num_chunks": len(chunks),
        "doc_type": doc_type,
        "tags": eval(tags) if tags else [],
        "language": eval(language) if language else ["vi"],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
        "questions": []
    }
    
    # Generate questions
    for idx, chunk in enumerate(chunks):
        print("LOG: Generating questions for chunk", idx + 1, "/", len(chunks), "...")
        questions_data = await document_service.create_question_embeddings(str(doc.id), idx, chunk, num_questions=3, is_appendix=True)
        response["questions"].append(questions_data)
        
    return response