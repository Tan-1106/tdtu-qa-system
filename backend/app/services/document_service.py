import re
import fitz
import shutil
import camelot
import tempfile
import pdfplumber
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
async def extract_pdf_document_content(file: UploadFile):
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
async def create_question_embeddings(doc_id: str, chunk_idx: int, chunk: str, num_questions: int = 5):
    generated_questions_list =  model_service.create_questions(chunk, num_questions=num_questions)

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

# Extract text and tables from a text-based PDF appendix
async def extract_pdf_appendix_content(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    if not text_process.is_text_based_pdf(tmp_path):
        raise RuntimeError("Appendix must be a text-based PDF.")
    
    try: 
        # Extract appendix description
        appendix_description = extract_appendix_description(tmp_path)
        appendix_description = text_process.normalize_text(appendix_description)
        
        # Extract tables using Camelot
        tables_data = []
        tables = camelot.read_pdf(tmp_path, pages='all', flavor='lattice')
        for table in tables:
            df = table.df
            df = df.map(text_process.clean_cell)
            tables_data.append(df.values.tolist())
        flattened_tables = [row for table in tables_data for row in table]
        
        # Delete duplicate
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

def extract_appendix_description(path: str) -> str:
    tables = camelot.read_pdf(path, pages='all', flavor='lattice')
    
    if not tables:
        with pdfplumber.open(path) as pdf:
            return '\n\n'.join(page.extract_text() or '' for page in pdf.pages).strip()
    
    tables_sorted = sorted(tables, key=lambda t: (t.page, -t._bbox[3]))
    first_table = tables_sorted[0]
    first_page_num = first_table.page
    
    with pdfplumber.open(path) as pdf:
        description_parts = []
        
        for page_idx in range(first_page_num - 1):
            page = pdf.pages[page_idx]
            text = page.extract_text() or ''
            description_parts.append(text)
        
        page = pdf.pages[first_page_num - 1]
        page_height = page.height
        
        cam_x0, cam_y0_bottom, cam_x1, cam_y1_top = first_table._bbox
        plumb_y0_top = page_height - cam_y1_top
        
        cropped_page = page.crop((0, 0, page.width, plumb_y0_top))
        above_text = cropped_page.extract_text() or ''
        description_parts.append(above_text)
        
        full_description = '\n\n'.join(description_parts).strip()
        
    return full_description

# Split appendix into chunks
async def split_appendix_into_chunks(description: str, tables: list[list[str]], table_header_rows: int) -> list[str]:
    chunks = []
    chunk_format = f"Description: {description}. Table header: "
    for i in range(0, table_header_rows):
        chunk_format += ' | '.join(tables[i])
        
    for i in range(table_header_rows, len(tables)):
        chunk = chunk_format + '. Content: ' + ' | '.join(tables[i])
        chunks.append(chunk)
        
    return chunks
