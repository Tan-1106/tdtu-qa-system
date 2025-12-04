from app.daos.document_chunk_dao import DocumentChunkDAO


async def store_document_chunks_record(document_chunks_record: dict):
    embedding = await DocumentChunkDAO().create_document_chunks_record(document_chunks_record)
    return embedding
    
    
# Delete document chunks by document ID
async def delete_document_chunks_by_doc_id(doc_id: str):
    await DocumentChunkDAO().delete_document_chunks_by_doc_id(doc_id)