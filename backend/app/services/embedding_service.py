import os
import re
import logging
from pyvi.ViTokenizer import tokenize
from fastapi.encoders import jsonable_encoder
from sentence_transformers import SentenceTransformer, CrossEncoder

from app.daos.embedding_dao import EmbeddingDAO


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


# --- SUPPORTING FUNCTIONS ---
# Get embedding for a given text
def get_embedding(text: str):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    text_tokenized = tokenize(text)
    embedding = embedding_model.encode(text_tokenized).tolist()

    return embedding


# Store embedding in the ChromaDB
async def store_embedding(text: str, metadatas: dict):
    embedding = get_embedding(text)
    embedding_data = {
        "vector": embedding,
        "metadatas": metadatas
    }
    embedding =  await EmbeddingDAO().create_embedding(embedding_data)
    return embedding
    
    
# Delete embeddings by document ID
async def delete_embeddings_by_doc_id(doc_id: str):
    await EmbeddingDAO().delete_embeddings_by_doc_id(doc_id)
    
    
# Reset embeddings collection
async def reset_embeddings():
    success = await EmbeddingDAO().reset_embeddings()
    return success