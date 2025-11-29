import re
import json
import fitz
import shutil
import camelot
import tempfile
import pdfplumber
import pytesseract
from fastapi import UploadFile
from tiktoken import get_encoding
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter


# # Token encoder
# enc = get_encoding("cl100k_base")


# # Chuẩn hóa văn bản
# def normalize_text(text: str):
#     if isinstance(text, str):
#         try:
#             data = json.loads(text)
#         except json.JSONDecodeError:
#             try:
#                 import ast
#                 data = ast.literal_eval(text)
#             except Exception:
#                 data = [text]
#     else:
#         data = text

#     if isinstance(data, list):
#         cleaned = []
#         for item in data:
#             if isinstance(item, str):
#                 s = item.replace("\n", " ")
#                 s = re.sub(r"\s+", " ", s).strip()
#                 cleaned.append(s)
#         return cleaned

#     if isinstance(data, str):
#         text = text.replace("\n", " ")
#         text = re.sub(r"\s+", " ", text).strip()
#         return text

#     return data


# # Chuẩn hóa ô trong bảng
# def normalize_cell(x):
#     x = str(x)
#     x = re.sub(r'[\n\r\t]+', '', x)
#     x = re.sub(r'\s{2,}', ' ', x)
#     return x.strip()


# # Kiểm tra PDF có phải là text-based không
# def is_text_based_pdf(file_path: str) -> bool:
#     try:
#         doc = fitz.open(file_path)
#         for page in doc:
#             page_text = page.get_text().strip()
#             if page_text:
#                 doc.close()
#                 return True
#         doc.close()
#         return False
#     except Exception as e:
#         raise RuntimeError("Failed to process PDF file.") from e


# # Truy xuất nội dung từ PDF document (text-based và scanned)
# async def extract_pdf_document_content(file: UploadFile):
#     document_content = ""
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = tmp.name
        
#     # Scanned
#     if not is_text_based_pdf(tmp_path):
#         try:
#             images = convert_from_path(tmp_path)
#             for img in images:
#                 page_text = pytesseract.image_to_string(img, lang='vie+eng')
#                 clean_text = re.sub(r'\s+', ' ', page_text)
#                 document_content += clean_text
#         except Exception as e:
#             raise RuntimeError("Failed to convert scanned PDF to text.") from e
        
#     # Text-based
#     else:
#         try:
#             doc = fitz.open(tmp_path)
#             for page in doc:
#                 page_text = page.get_text().strip()
#                 clean_text = re.sub(r'\s+', ' ', page_text)
#                 document_content += clean_text
#             doc.close()
#         except Exception as e:
#             raise RuntimeError("Failed to extract text from PDF.") from e
        
#     return document_content


# # Truy xuất nội dung từ PDF appendix
# async def extract_pdf_appendix_content(file: UploadFile):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = tmp.name
        
#     if not is_text_based_pdf(tmp_path):
#         raise RuntimeError("Appendix must be a text-based PDF.")
    
#     try: 
#         # Trích xuất phần mô tả phụ lục
#         appendix_description = extract_appendix_description(tmp_path)
#         appendix_description = normalize_text(appendix_description)
        
#         # Trích xuất bảng sử dụng Camelot
#         tables_data = []
#         tables = camelot.read_pdf(tmp_path, pages='all', flavor='lattice')
#         for table in tables:
#             df = table.df
#             df = df.map(normalize_cell)
#             tables_data.append(df.values.tolist())
#         flattened_tables = [row for table in tables_data for row in table]
        
#         # Xóa các hàng trùng lặp
#         unique_rows = []
#         seen = set()
        
#         for row in flattened_tables:
#             row_tuple = tuple(row)
#             if row_tuple not in seen:
#                 seen.add(row_tuple)
#                 unique_rows.append(row)        

#         return {
#             "description": appendix_description,
#             "tables": unique_rows
#         }
#     except Exception as e:
#         raise Exception("Lỗi khi trích xuất văn bản và bảng từ PDF phụ lục.") from e


# # Trích xuất phần mô tả phụ lục (văn bản trước bảng đầu tiên)
# def extract_appendix_description(path: str) -> str:
#     tables = camelot.read_pdf(path, pages='all', flavor='lattice')
    
#     if not tables:
#         with pdfplumber.open(path) as pdf:
#             return '\n\n'.join(page.extract_text() or '' for page in pdf.pages).strip()
    
#     tables_sorted = sorted(tables, key=lambda t: (t.page, -t._bbox[3]))
#     first_table = tables_sorted[0]
#     first_page_num = first_table.page
    
#     with pdfplumber.open(path) as pdf:
#         description_parts = []
        
#         for page_idx in range(first_page_num - 1):
#             page = pdf.pages[page_idx]
#             text = page.extract_text() or ''
#             description_parts.append(text)
        
#         page = pdf.pages[first_page_num - 1]
#         page_height = page.height
        
#         cam_x0, cam_y0_bottom, cam_x1, cam_y1_top = first_table._bbox
#         plumb_y0_top = page_height - cam_y1_top
        
#         cropped_page = page.crop((0, 0, page.width, plumb_y0_top))
#         above_text = cropped_page.extract_text() or ''
#         description_parts.append(above_text)
        
#         full_description = '\n\n'.join(description_parts).strip()
        
#     return full_description


# # Chia phụ lục thành các chunks
# async def split_appendix_into_chunks(description: str, tables: list[list[str]], table_header_rows: int) -> list[str]:
#     chunks = []
#     chunk_format = f"Description: {description}. Table header: "
#     for i in range(0, table_header_rows):
#         chunk_format += ' | '.join(tables[i])
        
#     for i in range(table_header_rows, len(tables)):
#         chunk = chunk_format + '. Content: ' + ' | '.join(tables[i])
#         chunks.append(chunk)
        
#     return chunks


# # Chia văn bản thành các chunks
# async def split_text_into_chunks(text: str, words_per_chunk: int, overlap: int) -> list[str]:
#     text = text.strip()
#     chunks = []
    
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=words_per_chunk,
#         chunk_overlap=overlap,
#         separators=[
#             "CHƯƠNG", "Chương",
#             "ĐIỀU", "Điều",
#             "MỤC", "Mục",
#             "I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X.", "XI.", "XII.", "XIII.", "XIV.", "XV.", "XVI.", "XVII.", "XVIII.", "XIX.", "XX.",
#             "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.", "14.", "15.", "16.", "17.", "18.", "19.", "20.",
#             "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)", "(10)", "(11)", "(12)", "(13)", "(14)", "(15)", "(16)", "(17)", "(18)", "(19)", "(20)",
#             ";", ".", "\n\n", "\n", " ", ""
            
#         ],
#         length_function=lambda x: len(enc.encode(x))
#     )
    
#     chunks = splitter.split_text(text)
    
#     # Gộp các chunks nhỏ
#     merged_chunks = await merge_chunks(chunks, target_max_length=words_per_chunk)
        
#     return merged_chunks


# # Gộp các chunks
# async def merge_chunks(chunks: list[str], target_max_length: int) -> list[str]:
#     # Lần đầu: gộp các chunks nhỏ
#     merged_chunks = []
#     current_chunk = ""

#     for chunk in chunks:
#         if len(enc.encode(current_chunk + " " + chunk)) <= target_max_length:
#             if current_chunk:
#                 current_chunk += " " + chunk
#             else:
#                 current_chunk = chunk
#         else:
#             if current_chunk:
#                 merged_chunks.append(current_chunk.strip())
#             current_chunk = chunk

#     if current_chunk:
#         merged_chunks.append(current_chunk.strip())

#     # Lần hai: đảm bảo không có các chunks quá nhỏ
#     final_chunks = []
#     buffer = ""
#     for chunk in merged_chunks:
#         if len(enc.encode(chunk)) < target_max_length * 0.5:
#             if buffer:
#                 buffer += " " + chunk
#             else:
#                 buffer = chunk
#         else:
#             if buffer:
#                 final_chunks.append(buffer.strip())
#                 buffer = ""
#             final_chunks.append(chunk.strip())

#     if buffer:
#         final_chunks.append(buffer.strip())

#     return final_chunks