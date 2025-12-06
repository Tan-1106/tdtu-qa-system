import os
import re
import fitz
import shutil
import asyncio
import aiofiles
import tempfile
import pytesseract
from fastapi import UploadFile
from tiktoken import get_encoding
from pdf2image import convert_from_path
from fastapi.encoders import jsonable_encoder
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.daos.document_dao import DocumentDAO


# --- CONFIGURATION ---
enc = get_encoding("cl100k_base")
UPLOAD_DIRECTORY = "uploads/documents"


# --- MAIN SERVICE FUNCTIONS ---
# Extract text content from PDF documents, handling both text-based and scanned PDFs.
async def extract_file_content(file: UploadFile):
    document_content = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Scanned
        is_text_pdf = await asyncio.to_thread(is_text_based_pdf, tmp_path)
        if not is_text_pdf:
            try:
                images = await asyncio.to_thread(convert_from_path, tmp_path)
                for img in images:
                    page_text = await asyncio.to_thread(pytesseract.image_to_string, img, 'vie+eng')
                    clean_text = re.sub(r'\s+', ' ', page_text)
                    document_content += clean_text
            except Exception as e:
                raise Exception("Failed to convert scanned PDF to text.") from e
            
        # Text-based
        else:
            try:
                # Run PDF text extraction in thread pool
                def extract_text_from_pdf(path):
                    doc = fitz.open(path)
                    content = ""
                    for page in doc:
                        page_text = page.get_text().strip()
                        clean_text = re.sub(r'\s+', ' ', page_text)
                        content += clean_text
                    doc.close()
                    return content
                
                document_content = await asyncio.to_thread(extract_text_from_pdf, tmp_path)
            except Exception as e:
                raise Exception("Failed to extract text from PDF.") from e
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        
    return document_content


# Split text into chunks for embedding
async def split_text_into_chunks(text: str, words_per_chunk: int, overlap: int) -> list[str]:
    text = text.strip()
    chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=words_per_chunk,
        chunk_overlap=overlap,
        separators=[
            "CHƯƠNG", "Chương",
            "ĐIỀU", "Điều",
            "MỤC", "Mục",
            "I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X.", "XI.", "XII.", "XIII.", "XIV.", "XV.", "XVI.", "XVII.", "XVIII.", "XIX.", "XX.",
            "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.", "14.", "15.", "16.", "17.", "18.", "19.", "20.",
            "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)", "(10)", "(11)", "(12)", "(13)", "(14)", "(15)", "(16)", "(17)", "(18)", "(19)", "(20)",
            ";", ".", "\n\n", "\n", " ", ""
            
        ],
        length_function=lambda x: len(enc.encode(x))
    )
    chunks = splitter.split_text(text)
    chunks = await merge_chunks(chunks, target_max_length=words_per_chunk)
    return chunks


# Save uploaded document file to server
async def save_document_file(file: UploadFile):
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    contents = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)
        
    return file_path


# Delete document file from server
async def delete_document_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


# Store document in MongoDB
async def store_document_record(document_record: dict):
    new_document = await DocumentDAO().create_document(document_record)
    return jsonable_encoder(new_document)


# Delete document record from MongoDB
async def delete_document_record(doc_id: str):
    await DocumentDAO().delete_document(doc_id)
    
    
# Get general documents with filters and pagination
async def get_general_documents(page: int, limit: int, doc_type: str, department: str, keyword: str):
    skip = (page - 1) * limit
    total = await DocumentDAO().count_general_documents(doc_type, department, keyword)
    total_pages = (total + limit - 1) // limit
    documents = await DocumentDAO().get_general_documents(skip, limit, doc_type, department, keyword)
    return {
        "documents": documents,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Get faculty documents with filters and pagination
async def get_faculty_documents(page: int, limit: int, doc_type: str, faculty: str, keyword: str):
    skip = (page - 1) * limit
    total = await DocumentDAO().count_faculty_documents(faculty, doc_type, keyword)
    total_pages = (total + limit - 1) // limit
    documents = await DocumentDAO().get_faculty_documents(faculty, skip, limit, doc_type, keyword)
    return {
        "documents": documents,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


# --- SUPPORTING FUNCTIONS ---
# check if PDF is text-based
def is_text_based_pdf(file_path: str) -> bool:
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                doc.close()
                return True
        doc.close()
        return False
    except Exception as e:
        raise RuntimeError("Failed to process PDF file.") from e
    
    
# Merge small chunks into larger ones
async def merge_chunks(chunks: list[str], target_max_length: int) -> list[str]:
    # First pass: merge small chunks
    merged_chunks = []
    current_chunk = ""
    for chunk in chunks:
        if len(enc.encode(current_chunk + " " + chunk)) <= target_max_length:
            if current_chunk:
                current_chunk += " " + chunk
            else:
                current_chunk = chunk
        else:
            if current_chunk:
                merged_chunks.append(current_chunk.strip())
            current_chunk = chunk
    if current_chunk:
        merged_chunks.append(current_chunk.strip())

    # Second pass: ensure no chunks are too small
    final_chunks = []
    buffer = ""
    for chunk in merged_chunks:
        if len(enc.encode(chunk)) < target_max_length * 0.5:
            if buffer:
                buffer += " " + chunk
            else:
                buffer = chunk
        else:
            if buffer:
                final_chunks.append(buffer.strip())
                buffer = ""
            final_chunks.append(chunk.strip())
    if buffer:
        final_chunks.append(buffer.strip())
    return final_chunks