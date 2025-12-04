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