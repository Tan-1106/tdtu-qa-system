from typing import Optional
from fastapi import UploadFile, Form
from fastapi.encoders import jsonable_encoder
from app.utils import text_process
from app.schemas import document_schema
from app.services import document_service, model_service

# Get all documents
async def get_documents():
    response = await document_service.get_documents()
    return response

# Get a document by ID
async def get_document_by_id(doc_id: str):
    response = await document_service.get_document_by_id(doc_id)
    return response

# Create a new document
async def create_document(doc_data: document_schema.DocumentCreate):
    doc_data = jsonable_encoder(doc_data)
    response = await document_service.create_document(doc_data)
    return response

# Update an existing document
async def update_document(doc_id: str, doc_update: document_schema.DocumentUpdate):
    update_data = jsonable_encoder(doc_update)
    if len(doc_update) == 1 and "edited_by" in doc_update:
            raise ValueError("No fields to update.")
    response = await document_service.update_document(doc_id, update_data)
    return response

# Delete a document by ID
async def delete_document(doc_id: str):
    response = await document_service.delete_document(doc_id)
    return response

# Upload a document
async def upload_document(
    file: UploadFile,
    title: str,
    doc_type: str,
    tags: Optional[str] = None,
    language: Optional[str] = Form('["vi"]'),
    file_url: str = Form(...)
):
    # Extract text from PDF
    print("LOG: Extracting text from PDF...")
    document_content = document_service.extract_pdf_document_content(file)
    
    # Split text into chunks
    print("LOG: Splitting text into chunks...")
    chunks = text_process.split_text_into_chunks(document_content, words_per_chunk=800, overlap=300)
    
    # Create document record in DB
    print("LOG: Creating document record in DB...")
    doc = await document_service.create_document({
        "title": title,
        "chunks": chunks,
        "doc_type": doc_type,
        "tags": eval(tags) if tags else [],
        "language": eval(language) if language else [],
        "file_url": file_url,
        "uploaded_by": "temp_user_id",
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
        "uploaded_by": "temp_user_id",
        "questions": []
    }
    # Generate questions
    print("LOG: Generating questions for each chunk...")
    for idx, chunk in enumerate(chunks):
        questions_data = await document_service.create_potential_questions(str(doc.id), idx, chunk)
        response["questions"].append(questions_data)

    # Embeddings
    print("LOG: Generating embeddings for questions...")
    for idx, generated_questions in enumerate(response["questions"]):
        for question_list in generated_questions["generated_questions"]:
            for question in question_list:
                embedding = await model_service.get_embedding(question)
                question_embedding = {
                    "vector": embedding,
                    "metadata": {"doc_id": str(doc.id), "chunk_index": idx}
                }
        