from app.daos import document_dao
from app.services import question_embedding_service

# Get all documents
async def get_documents():
    docs = await document_dao.get_documents()
    return docs

# Get a document by ID
async def get_document_by_id(doc_id: str):
    doc = await document_dao.get_document_by_id(doc_id)
    return doc

# Get a document chunk by doc_id and chunk_index
async def get_document_chunk(doc_id: str, chunk_index: int):
    chunk = await document_dao.get_document_chunk(doc_id, chunk_index)
    return chunk

# Get documents by type
async def get_documents_by_type(doc_type: str):
    docs = await document_dao.get_documents_by_type(doc_type)
    return docs

# Create a new document
async def create_document(doc_data: dict):
    doc = await document_dao.create_document(doc_data)
    return doc

# Update an existing document
async def update_document(doc_id: str, doc_update: dict):
    updated_doc = await document_dao.update_document(doc_id, doc_update)
    return updated_doc

# Delete a document by ID
async def delete_document(doc_id: str):
    deleted = await document_dao.delete_document(doc_id)
    if deleted:
        result = await question_embedding_service.delete_question_embeddings_by_doc_id(doc_id)
    
    return result

# View document file
async def view_document_file(doc_id: str):
    pass
    