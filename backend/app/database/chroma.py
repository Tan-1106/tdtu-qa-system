import os
import chromadb
from chromadb.config import Settings

chroma_host = os.getenv("CHROMA_HOST", "tdtu_qa_chromadb")
chroma_port = os.getenv("CHROMA_PORT", "8000")

client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(allow_reset=True)
)

# COLLECTIONS
# Question embeddings collection
question_embeddings_collection = client.get_or_create_collection(
    name="question_embeddings",
    metadata={"hnsw:space": "cosine"}
)

# Prototype collection
prototypes_collection = client.get_or_create_collection(
    name="prototypes",
    metadata={"hnsw:space": "cosine"}
)