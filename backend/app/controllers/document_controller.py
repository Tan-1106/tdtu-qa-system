from typing import Optional
from fastapi import UploadFile, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.utils import text_process
from app.schemas import document_schema
from app.services import document_service, prototype_service, question_embedding_service

# Get all documents
async def get_documents(filters: dict, skip: int, limit: int):
    docs = await document_service.get_documents(filters=filters, skip=skip, limit=limit)
    return docs

# Get a document by ID
async def get_document_by_id(doc_id: str):
    doc = await document_service.get_document_by_id(doc_id)
    return doc

# Get a document chunk by doc_id and chunk_index
async def get_document_chunk(doc_id: str, chunk_index: int):
    chunk = await document_service.get_document_chunk(doc_id, chunk_index)
    return chunk

# Get documents count
async def count_documents(filters: dict):
    count = await document_service.count_documents(filters=filters)
    return count

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
    doc_type: str,
    department: str,
    uploaded_by: str,
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...)
):
    # Extract text from PDF
    print("- LOG: Extracting text from PDF...")
    document_content = await text_process.extract_pdf_document_content(file)
    await file.seek(0)
    
    # Split text into chunks
    print("- LOG: Splitting text into chunks...")
    chunks = await text_process.split_text_into_chunks(document_content, words_per_chunk=800, overlap=200)
    
    # Save document to disk
    print("- LOG: Saving document to disk...")
    file_path = await document_service.save_document_file(file)
    
    # Create document record in DB
    print("- LOG: Creating document record in DB...")
    doc = await document_service.create_document({
        "title": file.filename,
        "file_path": file_path,
        "chunks": chunks,
        "doc_type": doc_type,
        "department": department,
        "language": eval(language) if language else [],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
    })
    
    # Prepare response and process document (generate questions, get embeddings, store embeddings in ChromaDB)
    response = {
        "doc_id": str(doc.id),
        "file_path": file_path,
        "title": file.filename,
        "chunks": chunks,
        "file_url": file_url,
        "questions": []
    }
    
    # Generate questions
    for idx, chunk in enumerate(chunks):
        print("- LOG: Generating questions for chunk", idx + 1, "/", len(chunks), "...")
        questions_data = await question_embedding_service.create_question_embeddings(str(doc.id), idx, chunk, num_questions=5)
        response["questions"].append(questions_data)
        
    # Cluster question embeddings
    print("- LOG: Clustering question embeddings...")
    await prototype_service.cluster_question_embeddings()

    return response

# Upload appendix document
async def upload_appendix_document(
    file: UploadFile,
    doc_type: str,
    department: str,
    uploaded_by: str,
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...)
):
    # Extract text and tables from PDF
    print("- LOG: Extracting text and tables from PDF appendix...")
    file_content = await text_process.extract_pdf_appendix_content(file)
    await file.seek(0)

    # Split appendix into chunks
    print("- LOG: Splitting appendix into chunks...")
    appendix_description = file_content["description"]
    tables = file_content["tables"]
    chunks = await text_process.split_appendix_into_chunks(appendix_description, tables, table_header_rows=2)
    
    # Save document to disk
    print("- LOG: Saving appendix document to disk...")
    file_path = await document_service.save_document_file(file)
    
    # Create document record in DB
    print("- LOG: Creating document record in DB...")
    doc = await document_service.create_document({
        "title": file.filename,
        "file_path": file_path,
        "chunks": chunks,
        "doc_type": doc_type,
        "department": department,
        "language": eval(language) if language else [],
        "file_url": file_url,
        "uploaded_by": uploaded_by,
    })

    # Prepare response and process document (generate questions, get embeddings, store embeddings in ChromaDB)
    response = {
        "doc_id": str(doc.id),
        "file_path": file_path,
        "title": file.filename,
        "file_url": file_url,
        "questions": []
    }
    
    # Generate questions
    for idx, chunk in enumerate(chunks):
        print("- LOG: Generating questions for chunk", idx + 1, "/", len(chunks), "...")
        questions_data = await question_embedding_service.create_question_embeddings(str(doc.id), idx, chunk, num_questions=3, is_appendix=True)
        response["questions"].append(questions_data)
        
    # Cluster question embeddings
    print("- LOG: Clustering question embeddings...")
    await prototype_service.cluster_question_embeddings()
        
    return response

# View a document
async def view_document_file(doc_id: str):
    file_name, file_content = await document_service.view_document_file(doc_id)
    
    return StreamingResponse(
        file_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={file_name}.pdf",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Security-Policy": "sandbox allow-scripts allow-same-origin",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-Download-Options": "noopen"
        }
    )
