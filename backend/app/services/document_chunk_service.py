from app.daos.document_chunk_dao import DocumentChunkDAO

# Store a new document chunks record
async def store_document_chunks_record(document_chunks_record: dict):
    embedding = await DocumentChunkDAO().create_document_chunks_record(document_chunks_record)
    return embedding
    
    
# Get document chunks by document ID
async def get_document_chunks(doc_id: str, page: int, limit: int):
    skip = (page - 1) * limit
    total = await DocumentChunkDAO().count_document_chunks(doc_id)
    total_pages = (total + limit - 1) // limit
    document_chunks = await DocumentChunkDAO().get_document_chunks(doc_id, skip, limit)
    return {
        "document_id": doc_id,
        "document_chunks": document_chunks,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
# Delete document chunks by document ID
async def delete_document_chunks_by_doc_id(doc_id: str):
    await DocumentChunkDAO().delete_document_chunks_by_doc_id(doc_id)