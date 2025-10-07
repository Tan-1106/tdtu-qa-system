import os
import torch
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

device = "cuda" if torch.cuda.is_available() else "cpu"

QUESTION_GENERATION_MODEL = os.getenv("QUESTION_GENERATION_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# Generate questions from a given text chunk
def create_questions(context: str):
    global device, QUESTION_GENERATION_MODEL
    tokenizer = AutoTokenizer.from_pretrained(QUESTION_GENERATION_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(QUESTION_GENERATION_MODEL, dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    model = model.to(device)
    input_ids = tokenizer.encode(context, return_tensors='pt', truncation=True, max_length=512).to(device)
    
    with torch.no_grad():
        sampling_outputs = model.generate(
            input_ids=input_ids,
            max_length=128,
            do_sample=True,
            temperature=0.5,
            top_p=0.8,
            top_k=20,
            num_return_sequences=5
        )
        
    results = []
    for output in sampling_outputs:
        question = tokenizer.decode(output, skip_special_tokens=True)
        results.append(question)
    
    return results 

# Get embedding for a given text
def get_embedding(text: str):
    global EMBEDDING_MODEL
    model = SentenceTransformer(EMBEDDING_MODEL)
    text_tokenized = tokenize(text)
    embedding = model.encode(text_tokenized).tolist()
    
    return embedding