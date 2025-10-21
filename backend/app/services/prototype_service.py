import hdbscan
import numpy as np
from typing import List
from sklearn.preprocessing import normalize
from fastapi.encoders import jsonable_encoder

from app.schemas import prototype_schema
from app.daos import question_embedding_dao, prototype_dao

# Get all prototypes
async def get_prototypes():
    prototypes = await prototype_dao.get_prototypes()
    return prototypes

# Get a prototype by ID
async def get_prototype_by_id(prototype_id: str):
    prototype = await prototype_dao.get_prototype_by_id(prototype_id)
    return prototype

# Create a prototype
async def create_prototype(prototype_data: dict):
    prototype = await prototype_dao.create_prototype(prototype_data)
    return prototype

# Cluster question embeddings and create prototypes
async def cluster_question_embeddings():
    # Fetch all question embeddings
    print("- LOG: Fetching question embeddings...")
    question_embeddings = await question_embedding_dao.get_question_embeddings()
    if not question_embeddings or len(question_embeddings) == 0:
        raise ValueError("No question embeddings available for clustering.")
    
    embeddings = np.array([qe['vector'] for qe in jsonable_encoder(question_embeddings)])
    embedding_ids = [qe['id'] for qe in jsonable_encoder(question_embeddings)]
    
    # Normalize embeddings to unit length if not already
    print("- LOG: Normalizing embeddings...")
    norms = np.linalg.norm(embeddings, axis=1)
    mean_norm = norms.mean()
    if mean_norm < 0.9 or mean_norm > 1.1:
        embeddings = normalize(embeddings, norm="l2")

    # Cluster embeddings using HDBSCAN
    print("- LOG: Clustering embeddings...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        min_samples=2,
        metric='euclidean',
        cluster_selection_epsilon=0.1
    )
    
    # Cluster and create prototypes
    cluster_labels = clusterer.fit_predict(embeddings)
    print(f"- LOG: Found {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)} clusters.")
    unique_labels = [l for l in np.unique(cluster_labels) if l != -1]
    
    prototypes: List[prototype_schema.PrototypeCreate] = []
    
    # Create prototypes for each cluster
    print("- LOG: Creating prototypes...")
    for label in unique_labels:
        cluster_indices = np.where(cluster_labels == label)[0]
        cluster_points = embeddings[cluster_indices]
        cluster_ids = [embedding_ids[i] for i in cluster_indices]
        
        # Calculate centroid
        centroid_vector = cluster_points.mean(axis=0).tolist()
        
        # Create prototype schema
        metadata = prototype_schema.PrototypeMetadata(question_embedding_ids=cluster_ids)
        prototype = prototype_schema.PrototypeCreate(
            centroid_vector=centroid_vector,
            metadata=metadata
        )
        prototypes.append(prototype)
        
    # Create prototypes in the database
    print("- LOG: Storing prototypes in database...")
    await prototype_dao.reset_prototypes_collection()
    for proto in prototypes:
        await prototype_dao.create_prototype(proto)
    
    return True

# Reset (Delete) prototypes collection
async def reset_prototypes_collection():
    result = await prototype_dao.reset_prototypes_collection()
    return result

# Semantic search prototypes
async def semantic_search_prototypes(query_vector: List[float], top_k: int = 5):
    prototypes = await prototype_dao.semantic_search_prototypes(query_vector, top_k)
    return prototypes