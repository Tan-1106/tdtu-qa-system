from app.services import embedding_service
from app.daos.document_dao import DocumentDAO
from app.utils.api_response import DatabaseException
from app.daos.document_chunk_dao import DocumentChunkDAO

# Store a new document chunks record
async def store_document_chunks_record(document_chunks_record: dict):
    embedding = await DocumentChunkDAO().create_document_chunks_record(document_chunks_record)
    return embedding
    
    
# Add a potential question for a specific chunk
async def add_potential_question(doc_id: str, chunk_index: int, question: str):
    chunks_record = await DocumentChunkDAO().get_document_chunks(doc_id, 0, 1000)
    if not chunks_record:
        raise DatabaseException(f"Document chunks record with doc_id {doc_id} not found")
    if str(chunk_index) not in chunks_record:
        raise DatabaseException(f"Chunk index {chunk_index} not found in document chunks for doc_id {doc_id}")
    
    new_embedding = await embedding_service.store_embedding(
        text=question,
        metadatas={
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "faculty": chunks_record[str(chunk_index)].get("faculty", "")
        }
    )
    
    chunks_record[str(chunk_index)]["potential_questions"].append(question)
    chunks_record[str(chunk_index)]["embedding_ids"].append(new_embedding["embedding_id"])
    await DocumentChunkDAO().update_document_chunks_record(doc_id, chunks_record)
    return chunks_record

    
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
    
    
# Get document chunk by document ID and chunk index
async def get_document_chunk_by_index(doc_id: str, chunk_index: int):
    file_name, file_url = await DocumentDAO().get_document_file_info(doc_id)
    chunk = await DocumentChunkDAO().get_document_chunk_by_index(doc_id, chunk_index)
    chunk["file_name"] = file_name
    chunk["file_url"] = file_url
    return chunk

    
# Delete document chunks by document ID
async def delete_document_chunks_by_doc_id(doc_id: str):
    await DocumentChunkDAO().delete_document_chunks_by_doc_id(doc_id)
    
    
# Delete a potential question for a specific chunk
async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int):
    chunks_record = await DocumentChunkDAO().get_document_chunks(doc_id, 0, 1000)
    if not chunks_record:
        raise DatabaseException(f"Document chunks record with doc_id {doc_id} not found")
    if str(chunk_index) not in chunks_record:
        raise DatabaseException(f"Chunk index {chunk_index} not found in document chunks for doc_id {doc_id}")
    if question_index < 0 or question_index >= len(chunks_record[str(chunk_index)]["potential_questions"]):
        raise DatabaseException(f"Question index {question_index} out of range for chunk index {chunk_index} in doc_id {doc_id}")
    
    # Remove the embedding from the database
    embedding_id = chunks_record[str(chunk_index)]["embedding_ids"][question_index]
    await embedding_service.delete_embedding_by_id(embedding_id)
    
    # Remove the question and embedding ID from the chunk record
    del chunks_record[str(chunk_index)]["potential_questions"][question_index]
    del chunks_record[str(chunk_index)]["embedding_ids"][question_index]
    
    await DocumentChunkDAO().update_document_chunks_record(doc_id, chunks_record)