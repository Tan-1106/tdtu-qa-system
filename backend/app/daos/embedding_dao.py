import uuid

from app.databases import chroma
from app.utils.api_response import DatabaseException

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
        all_data = chroma.embeddings_collection.get(include=["metadatas"])
        ids_to_delete = []
        
        for idx, metadata in enumerate(all_data["metadatas"]):
            if metadata.get("doc_id") == doc_id:
                ids_to_delete.append(all_data["ids"][idx])
        
        if ids_to_delete:
            chroma.embeddings_collection.delete(ids=ids_to_delete)
            
        
    # Delete embedding by embedding ID
    async def delete_embedding_by_id(self, embedding_id: str):
        chroma.embeddings_collection.delete(ids=[embedding_id])
            
            
    # Reset embeddings collection
    async def reset_embeddings(self):
        try:
            chroma.client.delete_collection(name="embeddings")
        except Exception:
            raise DatabaseException("Failed to reset embeddings collection.")
        chroma.embeddings_collection = chroma.client.get_or_create_collection(name="embeddings")
        return True
    
    
    # Semantic search embeddings
    async def semantic_search_embeddings(
        self,
        top_k: int,
        embedded_question: list[float],
        faculty: str
    ) -> list[dict]:
        # Build where filter based on faculty
        where_filter = None
        if faculty and faculty != "":
            where_filter = {
                "$or": [
                    {"faculty": faculty},
                    {"faculty": ""}
                ]
            }
        
        # Perform semantic search with ChromaDB
        results = chroma.embeddings_collection.query(
            query_embeddings=[embedded_question],
            n_results=top_k,
            where=where_filter,
            include=["metadatas", "distances"]
        )
        
        # Format results
        search_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for idx in range(len(results["ids"][0])):
                search_results.append({
                    "embedding_id": results["ids"][0][idx],
                    "metadata": results["metadatas"][0][idx],
                    "distance": results["distances"][0][idx]
                })
        
        return search_results
        