import os
import re
import fitz
import shutil
import camelot
import asyncio
import aiofiles
import tempfile
import pytesseract
from io import BytesIO
from fastapi import UploadFile
from pdf2image import convert_from_path
from fastapi.encoders import jsonable_encoder

from app.utils import text_process
from app.daos.document_dao import DocumentDAO


# --- CONFIGURATION ---
UPLOAD_DIRECTORY = "uploads/documents"


# --- SERVICE FUNCTIONS ---
# Extract text content from PDF documents, handling both text-based and scanned PDFs.
async def extract_file_content(file: UploadFile):
    document_content = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Scanned
        is_text_pdf = await asyncio.to_thread(text_process.is_text_based_pdf, tmp_path)
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


# Extract text and tables from appendix PDF documents
async def extract_pdf_appendix_content(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    if not text_process.is_text_based_pdf(tmp_path):
        raise RuntimeError("Appendix must be a text-based PDF.")
    
    try: 
        # Extract appendix description
        appendix_description = text_process.extract_appendix_description(tmp_path)
        appendix_description = text_process.normalize_text(appendix_description)
        
        # Extract tables using Camelot
        tables_data = []
        tables = camelot.read_pdf(tmp_path, pages='all', flavor='lattice')
        for table in tables:
            df = table.df
            df = df.map(text_process.normalize_cell)
            tables_data.append(df.values.tolist())
        flattened_tables = [row for table in tables_data for row in table]
        
        # Remove duplicate rows
        unique_rows = []
        seen = set()
        
        for row in flattened_tables:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_rows.append(row)        

        return {
            "description": appendix_description,
            "tables": unique_rows
        }
    except Exception as e:
        raise Exception("Failed to extract text and tables from appendix PDF.") from e


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
    

# Get document by ID
async def get_document_by_id(doc_id: str):
    document = await DocumentDAO().get_document_by_id(doc_id)
    return jsonable_encoder(document)


# Get all existing departments
async def get_all_existing_departments():
    departments = await DocumentDAO().get_all_existing_departments()
    return jsonable_encoder(departments)


# Get all existing doc types
async def get_all_existing_doc_types():
    doc_types = await DocumentDAO().get_all_existing_doc_types()
    return jsonable_encoder(doc_types)


# Update document record
async def update_document_record(doc_id: str, data: dict):
    updated_document = await DocumentDAO().update_document(doc_id, data)
    return jsonable_encoder(updated_document)


# View document file
async def view_document_file(doc_id: str):
    doc = await DocumentDAO().get_document_by_id(doc_id)
    doc = jsonable_encoder(doc)
        
    file_name = doc.get("file_name", "document.pdf")
    file_path = doc.get("file_path", "")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError("Document file not found")
    
    loop = asyncio.get_event_loop()
    file_content = await loop.run_in_executor(
        None,
        lambda: open(file_path, "rb").read()
    )
    
    return file_name, BytesIO(file_content)