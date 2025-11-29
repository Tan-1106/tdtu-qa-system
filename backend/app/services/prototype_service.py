import hdbscan
import numpy as np
from typing import List
from sklearn.preprocessing import normalize
from fastapi.encoders import jsonable_encoder

from app.schemas import prototype_schema
from app.daos import question_embedding_dao, prototype_dao


# # Lấy tất cả các prototype
# async def get_prototypes():
#     prototypes = await prototype_dao.get_prototypes()
#     return prototypes


# # Lấy một prototype theo ID
# async def get_prototype_by_id(prototype_id: str):
#     prototype = await prototype_dao.get_prototype_by_id(prototype_id)
#     return prototype


# # Tạo một prototype
# async def create_prototype(prototype_data: dict):
#     prototype = await prototype_dao.create_prototype(prototype_data)
#     return prototype


# # Phân cụm các embedding của câu hỏi để tạo prototypes
# async def cluster_question_embeddings():
#     await prototype_dao.reset_prototypes_collection()
    
#     # Lấy tất cả các embedding của câu hỏi
#     question_embeddings = await question_embedding_dao.get_question_embeddings()
#     if not question_embeddings or len(question_embeddings) == 0:
#         return False
    
#     embeddings = np.array([qe['vector'] for qe in jsonable_encoder(question_embeddings)])
#     embedding_ids = [qe['id'] for qe in jsonable_encoder(question_embeddings)]
    
#     # Chuẩn hóa các embedding về độ dài đơn vị nếu chưa được chuẩn hóa
#     norms = np.linalg.norm(embeddings, axis=1)
#     mean_norm = norms.mean()
#     if mean_norm < 0.9 or mean_norm > 1.1:
#         embeddings = normalize(embeddings, norm="l2")

#     # Phân cụm các embedding sử dụng HDBSCAN
#     clusterer = hdbscan.HDBSCAN(
#         min_cluster_size=500,
#         min_samples=10,
#         metric='euclidean',
#         cluster_selection_epsilon=0.1
#     )
    
#     # Phân cụm và tạo prototypes
#     cluster_labels = clusterer.fit_predict(embeddings)
#     print(f"- LOG: Found {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)} clusters.")
#     unique_labels = [l for l in np.unique(cluster_labels) if l != -1]
    
#     prototypes: List[prototype_schema.PrototypeCreate] = []
    
#     # Tạo prototypes cho mỗi cụm
#     for label in unique_labels:
#         cluster_indices = np.where(cluster_labels == label)[0]
#         cluster_points = embeddings[cluster_indices]
#         cluster_ids = [embedding_ids[i] for i in cluster_indices]
        
#         # Tính centroid
#         centroid_vector = cluster_points.mean(axis=0).tolist()
        
#         # Tạo prototype schema
#         metadata = prototype_schema.PrototypeMetadata(question_embedding_ids=cluster_ids)
#         prototype = prototype_schema.PrototypeCreate(
#             centroid_vector=centroid_vector,
#             metadata=metadata
#         )
#         prototypes.append(prototype)
        
#     noise_indices = np.where(cluster_labels == -1)[0]
#     if len(noise_indices) > 0:
#         noise_points = embeddings[noise_indices]
#         noise_ids = [embedding_ids[i] for i in noise_indices]

#         noise_centroid = noise_points.mean(axis=0).tolist()
#         noise_proto = {
#             "centroid_vector": noise_centroid,
#             "metadata": {"question_embedding_ids": noise_ids},
#         }
#         prototypes.append(noise_proto)
#         print(f"- LOG: Đã nhóm {len(noise_indices)} embedding chưa được gán vào một cụm còn lại.")
    
#     # Tạo prototypes trong cơ sở dữ liệu
#     for proto in prototypes:
#         await prototype_dao.create_prototype(proto)
#     prototype_dao.count_embeddings_per_prototype()
    
#     return True


# # Đặt lại collection prototypes
# async def reset_prototypes_collection():
#     result = await prototype_dao.reset_prototypes_collection()
#     return result


# # Tìm kiếm ngữ nghĩa cho prototypes
# async def semantic_search_prototypes(query_vector: List[float], top_k: int = 5):
#     prototypes = await prototype_dao.semantic_search_prototypes(query_vector, top_k)
#     return prototypes