from app.services import document_chunk_service

# Get document chunks by document ID
async def get_document_chunks(doc_id: str, page: int, limit: int):
    document_chunks = await document_chunk_service.get_document_chunks(doc_id, page, limit)
    return document_chunks