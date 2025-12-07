from app.services import document_chunk_service


# Get document chunks by document ID
async def get_document_chunks(doc_id: str, page: int, limit: int):
    document_chunks = await document_chunk_service.get_document_chunks(doc_id, page, limit)
    return document_chunks


# Add a potential question for a specific chunk
async def add_potential_question(doc_id: str, chunk_index: int, question: str):
    updated_chunk = await document_chunk_service.add_potential_question(doc_id, chunk_index, question)
    return updated_chunk


# Delete a potential question for a specific chunk
async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int):
    response = await document_chunk_service.delete_potential_question(doc_id, chunk_index, question_index)
    return response