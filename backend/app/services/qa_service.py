import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.daos.qa_dao import QADao



# --- CONFIGURATION ---
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "VietAI/envit5-translation")


translate_tokenizer = AutoTokenizer.from_pretrained(TRANSLATE_MODEL)
translate_model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATE_MODEL)


# --- SERVICE FUNCTIONS ---
# Create question record in the database
async def create_question_record(
    question: str,
    user_id: str,
    user_role: str,
    user_faculty: str
) -> dict:
    
    question_data = {
        "question": question,
        "user_id": user_id,
        "user_role": user_role,
        "user_faculty": user_faculty
    }
    question_record = await QADao().create_qa_record(question_data)
    return question_record