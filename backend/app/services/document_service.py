import re
import fitz
import shutil
import tempfile
import pytesseract
from fastapi import UploadFile
from pdf2image import convert_from_path
from app.daos import document_dao
from app.utils import text_process
from app.services import model_service
from app.services import question_embedding_service

# Get all documents
async def get_documents():
    docs = await document_dao.get_documents()
    return docs

# Get a document by ID
async def get_document_by_id(doc_id: str):
    doc = await document_dao.get_document_by_id(doc_id)
    return doc

# Create a new document
async def create_document(doc_data: dict):
    doc = await document_dao.create_document(doc_data)
    return doc

# Update an existing document
async def update_document(doc_id: str, doc_update: dict):
    updated_doc = await document_dao.update_document(doc_id, doc_update)
    return updated_doc

# Delete a document by ID
async def delete_document(doc_id: str):
    deleted = await document_dao.delete_document(doc_id)
    return deleted

# Extract text content from a PDF document (both text-based and scanned, not appendix)
def extract_pdf_document_content(file: UploadFile):
    document_content = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    # Scanned
    if not text_process.is_text_based_pdf(tmp_path):
        try:
            images = convert_from_path(tmp_path)
            for img in images:
                page_text = pytesseract.image_to_string(img, lang='vie+eng')
                clean_text = re.sub(r'\s+', ' ', page_text)
                document_content += clean_text
        except Exception as e:
            raise RuntimeError("Failed to convert scanned PDF to text.") from e
        
    # Text-based
    else:
        try:
            doc = fitz.open(tmp_path)
            for page in doc:
                page_text = page.get_text().strip()
                clean_text = re.sub(r'\s+', ' ', page_text)
                document_content += clean_text
            doc.close()
        except Exception as e:
            raise RuntimeError("Failed to extract text from PDF.") from e
        
    return document_content

# Generate potential questions for a text chunk
async def create_question_embeddings(doc_id: str, chunk_idx: int, chunk: str):
    generated_questions_list =  model_service.create_questions(chunk)
    
    print("LOG: Create embeddings for questions...")
    for question in generated_questions_list:
        embedding = model_service.get_embedding(question)
        question_embedding = {
            "vector": embedding,
            "metadata": {"doc_id": doc_id, "chunk_index": chunk_idx}
        }
        await question_embedding_service.create_question_embedding(question_embedding)

    return {
        "doc_id": doc_id,
        "chunk_index": chunk_idx,
        "questions_list": generated_questions_list
    }

# Extract text and tables from a text-based PDF appendix (LATER)
# async def extract_pdf_appendix_content(file: UploadFile):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = tmp.name
        
#     text = ""
#     tables_data = []
    
#     if not is_text_based_pdf(tmp_path):
#         raise RuntimeError("Appendix must be a text-based PDF.")
#     else:
#         try:
#             # Extract tables
#             tables = camelot.read_pdf(tmp_path, pages='all')
            
#             doc = fitz.open(tmp_path)
#             for i, page in enumerate(doc, start=1):
#                 page_text = page.get_text().strip()
#                 clean_text = re.sub(r'\s+', ' ', page_text)
#                 text += f"\n\n[PAGE {i}]\n{clean_text}"

#                 # Add table(s) from this page if available
#                 page_tables = [t for t in tables if t.page == i]
#                 for t in page_tables:
#                     df = t.df.applymap(normalize_cell)
#                     tables_data.append(df.values.tolist())
#             doc.close()
#         except Exception as e:
#             raise RuntimeError("Failed to extract text from PDF.") from e
#         pass