import re
import fitz
import shutil
import camelot
import tempfile
import pytesseract
from typing import Optional
from fastapi import UploadFile
from pdf2image import convert_from_path
from app.utils.document_upload import is_text_based_pdf, normalize_cell

# Extract text content from a PDF document (both text-based and scanned)
async def extract_pdf_document_content(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    # Check if the PDF is text-based or scanned
    text = ""
    # If scanned, use OCR to extract text
    if not is_text_based_pdf(tmp_path):
        try:
            images = convert_from_path(tmp_path)
            for img in images:
                page_text = pytesseract.image_to_string(img, lang='vie+eng')
                clean_text = re.sub(r'\s+', ' ', page_text)
                text += f"\n\n[PAGE]\n{clean_text}"
        except Exception as e:
            raise RuntimeError("Failed to convert scanned PDF to text.") from e
        
    # If text-based, extract text directly
    else:
        try:
            doc = fitz.open(tmp_path)
            for i, page in enumerate(doc, start=1):
                page_text = page.get_text().strip()
                clean_text = re.sub(r'\s+', ' ', page_text)
                text += f"\n\n[PAGE {i}]\n{clean_text}"
            doc.close()
        except Exception as e:
            raise RuntimeError("Failed to extract text from PDF.") from e
    return {
        "text": text
    }
    
#Upload document
async def upload_document(
    file_content: str,
    title: str,
    doc_type: str,
    tags: Optional[str],
    language: Optional[str],
    file_url: str
):
    pass
    
    
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