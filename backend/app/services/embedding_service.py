import os
import re
import asyncio
import logging
from pyvi.ViTokenizer import tokenize
from fastapi.encoders import jsonable_encoder
from sentence_transformers import SentenceTransformer

from app.daos.document_dao import DocumentDAO
from app.daos.embedding_dao import EmbeddingDAO
from app.daos.document_chunk_dao import DocumentChunkDAO


logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


# --- CONFIGURATION ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "dangvantuan/vietnamese-embedding")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


# --- MAIN SERVICE FUNCTIONS ---
# Get embedding vectors with pagination
async def get_embedding_vectors(page: int, limit: int):
    skip = (page - 1) * limit
    total = await EmbeddingDAO().count_embeddings()
    total_pages = (total + limit - 1) // limit
    vectors = await EmbeddingDAO().get_embedding_vectors(skip, limit)
    return {
        "vectors": vectors,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Store embedding in the ChromaDB
async def store_embedding(text: str, metadatas: dict):
    embedding = await get_embedding(text)
    embedding_data = {
        "vector": embedding,
        "metadatas": metadatas
    }
    embedding =  await EmbeddingDAO().create_embedding(embedding_data)
    return embedding


# Reset embeddings collection
async def reset_embeddings():
    success = await EmbeddingDAO().reset_embeddings()
    return success


# Recreate embeddings for document chunks
async def recreate_embeddings():
    await EmbeddingDAO().reset_embeddings()
    document_chunks_records = jsonable_encoder(await DocumentChunkDAO().get_all_document_chunks())
    
    for chunks_record in document_chunks_records:
        doc_id = chunks_record["doc_id"]
        document = jsonable_encoder(await DocumentDAO().get_document_by_id(doc_id))
        
        chunks = chunks_record["chunks"]
        for chunk_index_str, chunk in chunks.items():
            chunk_index = int(chunk_index_str)
            potential_questions = chunk["potential_questions"]
            
            for embedding_id_index, text in enumerate(potential_questions):
                embedding = await get_embedding(text)
                embedding_data = {
                    "vector": embedding,
                    "metadatas": {
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "faculty": document["faculty"] if document["faculty"] else ""
                    }
                }
                
                new_embedding = await EmbeddingDAO().create_embedding(embedding_data)
                await DocumentChunkDAO().update_chunk_embedding_id(
                    doc_id,
                    chunk_index,
                    embedding_id_index,
                    new_embedding["embedding_id"]
                )
    

# Delete embeddings by ID
async def delete_embedding_by_id(embedding_id: str):
    await EmbeddingDAO().delete_embedding_by_id(embedding_id)
    
    
# Semantic search embeddings
async def find_relevant_potential_questions(
    top_k: int,
    embedding_vector: list[float],
    user_faculty: str
):
    potenial_question_embeddings = await EmbeddingDAO().semantic_search_embeddings(
        top_k = top_k,
        embedded_question = embedding_vector,
        faculty = user_faculty
    )
    return potenial_question_embeddings

# --- SUPPORTING FUNCTIONS ---
# Get embedding for a given text
async def get_embedding(text: str):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    text_tokenized = await asyncio.to_thread(tokenize, text)
    embedding_vector = await asyncio.to_thread(embedding_model.encode, text_tokenized)
    embedding = embedding_vector.tolist()

    return embedding

# Delete embeddings by document ID
async def delete_embeddings_by_doc_id(doc_id: str):
    await EmbeddingDAO().delete_embeddings_by_doc_id(doc_id)