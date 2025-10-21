import uuid
import json
from fastapi.encoders import jsonable_encoder

from app.databases import chroma
from app.schemas import prototype_schema

# Read all prototypes
async def get_prototypes() -> list[prototype_schema.PrototypeResponse]:
    results = chroma.prototypes_collection.get(include=["embeddings", "metadatas"])
    if not results or 'ids' not in results:
        return []
    
    prototypes = []
    for idx in range(len(results['ids'])):
        metadata = {k: json.loads(v) for k, v in results['metadatas'][idx].items()}
        
        prototypes.append(
            prototype_schema.PrototypeResponse(
                id=results['ids'][idx],
                centroid_vector=results['embeddings'][idx],
                metadata=metadata
            )
        )
        
    return prototypes

# Read a prototype by ID
async def get_prototype_by_id(prototype_id: str) -> prototype_schema.PrototypeResponse:
    results = chroma.prototypes_collection.get(ids=[prototype_id], include=["embeddings", "metadatas"])
    if not results or 'ids' not in results or len(results['ids']) == 0:
        raise ValueError("Prototype not found.")
    
    metadata = {k: json.loads(v) for k, v in results['metadatas'][0].items()}
    
    return prototype_schema.PrototypeResponse(
        id=results['ids'][0],
        centroid_vector=results['embeddings'][0],
        metadata=metadata
    )
    
# Create a new prototype
async def create_prototype(prototype_data: prototype_schema.PrototypeCreate) -> prototype_schema.PrototypeResponse:
    prototype_data = jsonable_encoder(prototype_data)    
    prototype_id = str(uuid.uuid4())

    metadata_serialized = {k: json.dumps(v) for k, v in prototype_data["metadata"].items()}

    chroma.prototypes_collection.add(
        ids=[prototype_id],
        embeddings=[prototype_data["centroid_vector"]],
        metadatas=[metadata_serialized],
    )
    
    return prototype_schema.PrototypeResponse(
        id=prototype_id,
        centroid_vector=prototype_data["centroid_vector"],
        metadata=prototype_data["metadata"]
    )
    
# Reset (delete) prototypes collection
async def reset_prototypes_collection() -> bool:
    try:
        chroma.client.delete_collection("prototypes")
        chroma.prototypes_collection = chroma.client.create_collection("prototypes")
        return True
    except Exception as e:
        print(f"Error resetting prototypes collection: {e}")
        return False
    
# Semantic search for prototypes
async def semantic_search_prototypes(query_vector: list[float], top_k: int = 3) -> list[prototype_schema.PrototypeResponse]:
    results = chroma.prototypes_collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["embeddings", "metadatas"]
    )
    
    if not results or 'ids' not in results or len(results['ids']) == 0:
        return []
    
    prototypes = []
    for idx in range(len(results['ids'][0])):
        metadata = {k: json.loads(v) for k, v in results['metadatas'][0][idx].items()}
        
        prototypes.append(
            prototype_schema.PrototypeResponse(
                id=results['ids'][0][idx],
                centroid_vector=results['embeddings'][0][idx],
                metadata=metadata
            )
        )
        
    return prototypes