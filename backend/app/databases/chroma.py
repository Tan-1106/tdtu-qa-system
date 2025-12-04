import os
import chromadb
from chromadb.config import Settings


# --- CONFIGURATION ---
chroma_host = os.getenv("CHROMA_HOST", "tdtu_qa_chromadb")
chroma_port = os.getenv("CHROMA_PORT", "8000")


# --- CLIENT ---
client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(allow_reset=True)
)


# --- COLLECTIONS ---
# Question embeddings collection
embeddings_collection = client.get_or_create_collection(
    name="embeddings",
    metadata={"hnsw:space": "cosine"}
)