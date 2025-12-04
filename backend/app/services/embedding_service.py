import os
import re
import logging
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer, CrossEncoder

from app.daos.embedding_dao import EmbeddingDAO


logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


# --- CONFIGURATION ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "dangvantuan/vietnamese-embedding")


embedding_model = SentenceTransformer(EMBEDDING_MODEL)


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