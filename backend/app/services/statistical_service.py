import hdbscan
from fastapi.encoders import jsonable_encoder

from app.daos.qa_dao import QADao
from app.utils.api_response import UserError
from app.daos.statistical_dao import StatisticalDao
from app.services import embedding_service, llm_service, qa_service


# --- SERVICE FUNCTIONS ---
# Common question statistics
async def popular_questions_statistics(period_type: str, n: int):
    # Get QA records by period type
    qa_records = jsonable_encoder(await QADao().get_qa_records_by_period_type(period_type))
    questions = [record["question"] for record in qa_records]
    
    # Get embeddings for questions
    embedding_questions = []
    for question in questions:
        embedding = await embedding_service.get_embedding(question)
        embedding_questions.append(embedding)
        
    # Cluster embeddings
    labels = cluster_embeddings(embedding_questions)
    cluster_dict = {}
    for idx, label in enumerate(labels):
        if label not in cluster_dict:
            cluster_dict[label] = {
                "questions": [],
                "count": 0
            }
        cluster_dict[label]["questions"].append(questions[idx])
        cluster_dict[label]["count"] += 1
        
    # Get top N popular questions
    sorted_clusters = sorted(cluster_dict.items(), key=lambda x: x[1]["count"], reverse=True)
    top_n_clusters = sorted_clusters[:n]
        
    # Generate general questions for top N clusters
    api_key = await llm_service.get_current_api_key()
    if not api_key:
        raise UserError("No active API key found. Please activate an API key to proceed.")
    
    popular_questions = []
    for label, data in top_n_clusters:
        general_question = await llm_service.get_general_question(api_key, data["questions"])
        popular_questions.append({
            "question": general_question,
            "count": data["count"],
        })
        
    # Get answer for each popular question
    for item in popular_questions:
        answer = await qa_service.get_answer(item["question"], item["question"], "", "vi")
        item["answer"] = answer
        
    # Store popular questions statistics record
    result = await StatisticalDao().store_popular_questions(popular_questions)
    return jsonable_encoder(result)


# # Get popular questions statistics records
async def get_popular_questions():
    result = await StatisticalDao().get_popular_questions()
    return jsonable_encoder(result)
    

# --- SUPPORTING FUNCTIONS ---
# Cluster embeddings using HDBSCAN
def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,             
        min_samples=1,                  
        metric='euclidean',             
        cluster_selection_epsilon=0.3,  
        cluster_selection_method='eom'  
    )
    labels = clusterer.fit_predict(embeddings)
    return labels


# Get total questions
async def questions_statistics(period_type: str):
    count = await QADao().questions_statistics(period_type)
    return count