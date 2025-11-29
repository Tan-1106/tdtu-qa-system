import uuid
import json
from fastapi.encoders import jsonable_encoder

from app.databases import chroma
from app.schemas import prototype_schema


# # Lấy tất cả các prototype
# async def get_prototypes() -> list[prototype_schema.PrototypeResponse]:
#     results = chroma.prototypes_collection.get(include=["embeddings", "metadatas"])
#     if not results or 'ids' not in results:
#         return []
    
#     prototypes = []
#     for idx in range(len(results['ids'])):
#         metadata = {k: json.loads(v) for k, v in results['metadatas'][idx].items()}
        
#         prototypes.append(
#             prototype_schema.PrototypeResponse(
#                 id=results['ids'][idx],
#                 centroid_vector=results['embeddings'][idx],
#                 metadata=metadata
#             )
#         )
        
#     return prototypes


# # Lấy một prototype theo ID
# async def get_prototype_by_id(prototype_id: str) -> prototype_schema.PrototypeResponse:
#     results = chroma.prototypes_collection.get(ids=[prototype_id], include=["embeddings", "metadatas"])
#     if not results or 'ids' not in results or len(results['ids']) == 0:
#         raise ValueError("Không tìm thấy prototype.")
    
#     metadata = {k: json.loads(v) for k, v in results['metadatas'][0].items()}
    
#     return prototype_schema.PrototypeResponse(
#         id=results['ids'][0],
#         centroid_vector=results['embeddings'][0],
#         metadata=metadata
#     )
    
# # Tạo một prototype mới
# async def create_prototype(prototype_data: prototype_schema.PrototypeCreate) -> prototype_schema.PrototypeResponse:
#     prototype_data = jsonable_encoder(prototype_data)    
#     prototype_id = str(uuid.uuid4())

#     metadata_serialized = {k: json.dumps(v) for k, v in prototype_data["metadata"].items()}

#     chroma.prototypes_collection.add(
#         ids=[prototype_id],
#         embeddings=[prototype_data["centroid_vector"]],
#         metadatas=[metadata_serialized],
#     )
    
#     return prototype_schema.PrototypeResponse(
#         id=prototype_id,
#         centroid_vector=prototype_data["centroid_vector"],
#         metadata=prototype_data["metadata"]
#     )
    
    
# # Đăng ký lại (reset) collection prototypes
# async def reset_prototypes_collection() -> bool:
#     try:
#         chroma.client.delete_collection("prototypes")
#         chroma.prototypes_collection = chroma.client.create_collection("prototypes")
#         return True
#     except Exception as e:
#         print(f"Error resetting prototypes collection: {e}")
#         return False
    
    
# # Tìm kiếm ngữ nghĩa cho prototypes
# async def semantic_search_prototypes(query_vector: list[float], top_k: int = 3) -> list[prototype_schema.PrototypeResponse]:
#     results = chroma.prototypes_collection.query(
#         query_embeddings=[query_vector],
#         n_results=top_k,
#         include=["embeddings", "metadatas"]
#     )
    
#     if not results or 'ids' not in results or len(results['ids']) == 0:
#         return []
    
#     prototypes = []
#     for idx in range(len(results['ids'][0])):
#         metadata = {k: json.loads(v) for k, v in results['metadatas'][0][idx].items()}
        
#         prototypes.append(
#             prototype_schema.PrototypeResponse(
#                 id=results['ids'][0][idx],
#                 centroid_vector=results['embeddings'][0][idx],
#                 metadata=metadata
#             )
#         )
        
#     return prototypes


# # (Hàm hỗ trợ)
# # Duyệt tất cả các prototype và đếm có bao nhiêu embedding câu hỏi được phân cụm vào mỗi prototype
# def count_embeddings_per_prototype(batch_size: int = 1000, verbose: bool = True):
#     counts: list[dict] = []
#     try:
#         offset = 0
#         while True:
#             res = chroma.prototypes_collection.get(include=["metadatas"], limit=batch_size, offset=offset)
#             ids = res.get("ids", []) or []
#             metas = res.get("metadatas", []) or []

#             if not ids:
#                 break

#             for i, pid in enumerate(ids):
#                 meta = metas[i] or {}
#                 raw = meta.get("question_embedding_ids")
#                 if raw is None:
#                     n = 0
#                 else:
#                     if isinstance(raw, str):
#                         try:
#                             items = json.loads(raw)
#                             n = len(items) if isinstance(items, list) else 0
#                         except Exception:
#                             n = 0
#                     elif isinstance(raw, list):
#                         n = len(raw)
#                     else:
#                         n = 0

#                 counts.append({"id": pid, "count": n})
#                 if verbose:
#                     print(f"- Prototype {pid}: {n} embeddings được phân cụm")

#             offset += len(ids)

#         if verbose:
#             total = sum(c["count"] for c in counts)
#             num = len(counts)
#             if num:
#                 avg = total / num
#                 print(f"Tóm tắt -> Prototypes: {num}, Tổng số embeddings được phân cụm: {total}, Trung bình mỗi prototype: {avg:.2f}")
#             else:
#                 print("Không tìm thấy prototype nào.")

#     except Exception as e:
#         if verbose:
#             print(f"Lỗi khi đếm embeddings cho mỗi prototype: {e}")
#     return counts