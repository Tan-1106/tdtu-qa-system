import re
import fitz
import shutil
import camelot
import tempfile
import pytesseract
from typing import Optional
from fastapi import UploadFile
from pdf2image import convert_from_path
from app.daos import document_dao
from app.services.model_service import create_questions, get_embedding
from app.daos import question_embedding_dao as question_embedding_crud
from app.utils.document_process import is_text_based_pdf, split_text_into_chunks
from app.schemas.question_embedding_schema import QuestionEmbeddingCreate, QuestionEmbeddingMetadata

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
async def delete_document(doc_id: str) -> bool:
    deleted = await document_dao.delete_document(doc_id)
    return deleted

# Extract text content from a PDF document (both text-based and scanned)
# async def extract_pdf_document_content(file: UploadFile):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = tmp.name
        
#     text = ""
#     # Scanned
#     if not is_text_based_pdf(tmp_path):
#         try:
#             images = convert_from_path(tmp_path)
#             for img in images:
#                 page_text = pytesseract.image_to_string(img, lang='vie+eng')
#                 clean_text = re.sub(r'\s+', ' ', page_text)
#                 text += clean_text
#         except Exception as e:
#             raise RuntimeError("Failed to convert scanned PDF to text.") from e
        
#     # Text-based
#     else:
#         try:
#             doc = fitz.open(tmp_path)
#             for page in doc:
#                 page_text = page.get_text().strip()
#                 clean_text = re.sub(r'\s+', ' ', page_text)
#                 text += clean_text
#             doc.close()
#         except Exception as e:
#             raise RuntimeError("Failed to extract text from PDF.") from e
#     return text

# # Process document
# async def process_document(
#     file_content: str,
#     title: str,
#     doc_type: str,
#     tags: Optional[str],
#     language: Optional[str],
#     file_url: str
# ) -> DocumentResponse:
#     # Split text into chunks
#     chunks = split_text_into_chunks(file_content, words_per_chunk=300, overlap=100)
    
#     # Upload document to database
#     doc_data = {
#         "title": title,
#         "chunks": chunks,
#         "doc_type": doc_type,
#         "tags": eval(tags) if tags else [],
#         "language": eval(language) if language else [],
#         "file_url": file_url,
#         "uploaded_by": "temp_user_id",
#     }

#     # Save document metadata to database
#     doc = await document_dao.create_document(doc_data)
#     if not doc:
#         raise RuntimeError("Failed to save document to database.")
    
#     # Generate potential questions for each chunk and their embeddings
#     chunk_idx = 0
#     print("="*100)
#     print(f"Creating questions...({chunk_idx+1}/{len(chunks)})")
#     for chunk in chunks:
#         questions = create_questions(chunk)
        
#         for q in questions:
#             emb = get_embedding(q)
            
#             print("Converting question to embedding and saving to DB...")
#             qe = {
#                 "vector": emb,
#                 "metadata": {
#                     "doc_id": str(doc.id),
#                     "chunk_index": chunk_idx
#                 }
#             }
#             await question_embedding_crud.create_question_embedding(qe)
            
#         chunk_idx += 1

#     return DocumentResponse(**doc.model_dump())
    
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