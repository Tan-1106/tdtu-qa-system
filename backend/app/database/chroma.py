import os
import chromadb

def get_chroma_collection(name: str = "tdtu_docs"):
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_port = os.getenv("CHROMA_PORT", "8000")
    chroma_path = os.getenv("CHROMA_PATH", "/data/chroma")

    if chroma_host:
        # Kết nối qua HTTP
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        try:
            return client.get_collection(name)
        except Exception:
            return client.create_collection(name)
    else:
        # Kết nối local persistent
        client = chromadb.PersistentClient(path=chroma_path)
        return client.get_or_create_collection(name)