import uuid
from bson import ObjectId
from datetime import datetime, timezone

from app.databases import chroma
from app.utils import serializer
from app.utils.api_response import DatabaseException
from app.utils.basic_information import Role, Faculty

class EmbeddingDAO:
    # Create a new embedding
    async def create_embedding(self, embedding: dict) -> dict:        
        embedding_id = str(uuid.uuid4())
        chroma.embeddings_collection.add(
            ids=[embedding_id],
            embeddings=[embedding["vector"]],
            metadatas=[embedding["metadatas"]]
        )
        return {
            "embedding_id": embedding_id,
            "vector": embedding["vector"],
            "metadatas": embedding["metadatas"]
        }
        
        
    # Count total embeddings
    async def count_embeddings(self) -> int:
        count = chroma.embeddings_collection.count()
        return count
    
    
    # Get embedding vectors with pagination
    async def get_embedding_vectors(self, skip: int, limit: int) -> list:
        all_embeddings = chroma.embeddings_collection.get(
            include=["embeddings", "metadatas"],
            offset=skip,
            limit=limit
        )
        embeddings_list = []
        for idx in range(len(all_embeddings["ids"])):
            vector = all_embeddings["embeddings"][idx]
            if hasattr(vector, 'tolist'):
                vector = vector.tolist()
            
            embedding_data = {
                "embedding_id": all_embeddings["ids"][idx],
                "vector": vector,
                "metadatas": all_embeddings["metadatas"][idx]
            }
            embeddings_list.append(embedding_data)
        return embeddings_list
        
    
    # Delete embeddings by document ID
    async def delete_embeddings_by_doc_id(self, doc_id: str):
        # Retrieve all embeddings metadata
        all_metadatas = chroma.embeddings_collection.get(include=["metadatas"])
        ids_to_delete = []
        
        for idx, metadata in enumerate(all_metadatas):
            if metadata.get("doc_id") == doc_id:
                ids_to_delete.append(chroma.embeddings_collection.get(include=["ids"])["ids"][idx])
        
        if ids_to_delete:
            chroma.embeddings_collection.delete(ids=ids_to_delete)
            
            
    # Reset embeddings collection
    async def reset_embeddings(self):
        try:
            chroma.client.delete_collection(name="embeddings")
        except Exception:
            raise DatabaseException("Failed to reset embeddings collection.")
        chroma.embeddings_collection = chroma.client.get_or_create_collection(name="embeddings")
        return True