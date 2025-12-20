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
    start_date, end_date, qa_records = jsonable_encoder(await QADao().get_qa_records_by_period_type(period_type))
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
            "summary": {
                "faculty_scope": None,
                "start_date": start_date,
                "end_date": end_date,
                "count": data["count"],
            },
            "is_display": False
        })
        
    # Get answer for each popular question
    for item in popular_questions:
        answer = await qa_service.get_answer(item["question"], item["question"], "", "vi")
        item["answer"] = answer
        
    # Store popular questions statistics record
    result = await StatisticalDao().store_popular_questions(popular_questions)
    return jsonable_encoder(result)


# Toggle popular question display status
async def toggle_popular_question_display(question_id: str):
    updated_question = await StatisticalDao().toggle_popular_question_display(question_id)
    return jsonable_encoder(updated_question)


# Get popular questions statistics records
async def get_popular_questions(page: int, limit: int, is_display: bool, faculty: str = None):
    skip = (page - 1) * limit
    total = await StatisticalDao().count_popular_questions(is_display, faculty)
    total_pages = (total + limit - 1) // limit
    result = await StatisticalDao().get_popular_questions(skip, limit, is_display, faculty)
    return {
        "popular_questions": jsonable_encoder(result),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


# Get popular question statistics records for student
async def get_popular_questions_student(page: int, limit: int, faculty: str, faculty_only: bool):
    skip = (page - 1) * limit
    total = await StatisticalDao().count_popular_questions_student(faculty, faculty_only)
    total_pages = (total + limit - 1) // limit
    result = await StatisticalDao().get_popular_questions_student(skip, limit, faculty, faculty_only)
    return {
        "popular_questions": jsonable_encoder(result),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Assign faculty scope to popular question
async def assign_faculty_scope_to_popular_question(question_id: str, faculty: str):
    updated_question = await StatisticalDao().assign_faculty_scope_to_popular_question(question_id, faculty)
    return jsonable_encoder(updated_question)


# Update popular question
async def update_popular_question(question_id: str, update_data: dict):
    updated_question = await StatisticalDao().update_popular_question(question_id, update_data)
    return jsonable_encoder(updated_question)
    

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


# Get popular question by ID
async def get_popular_question_by_id(question_id: str):
    result = await StatisticalDao().get_popular_question_by_id(question_id)
    return jsonable_encoder(result)