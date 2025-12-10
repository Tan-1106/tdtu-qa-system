import re
import ast
import json
import fitz
import camelot
import pdfplumber
from tiktoken import get_encoding
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --- CONFIGURATION ---
enc = get_encoding("cl100k_base")


# --- SUPPORTING FUNCTIONS ---
# Normalize table cell content
def normalize_cell(x):
    x = str(x)
    x = re.sub(r'[\n\r\t]+', '', x)
    x = re.sub(r'\s{2,}', ' ', x)
    return x.strip()


# Normalize text input
def normalize_text(text: str):
    if isinstance(text, str):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:python)?|```$", "", cleaned, flags=re.IGNORECASE).strip()
        try:
            data = json.loads(cleaned)
        except Exception:
            try:
                data = ast.literal_eval(cleaned)
            except Exception:
                data = cleaned
    else:
        data = text

    if isinstance(data, list):
        out = []
        for item in data:
            if isinstance(item, str):
                s = re.sub(r"[ \t]+", " ", item).strip()
                out.append(s)
        return out

    if isinstance(data, str):
        return re.sub(r"[ \t]+", " ", data).strip()

    return data


# Extract appendix description from PDF
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


# Split appendix description and tables into chunks
async def split_appendix_into_chunks(description: str, tables: list[list[str]], table_header_rows: int) -> list[str]:
    chunks = []
    chunk_format = f"Description: {description}. Table header: "
    for i in range(0, table_header_rows):
        chunk_format += ' | '.join(tables[i])
        
    for i in range(table_header_rows, len(tables)):
        chunk = chunk_format + '. Content: ' + ' | '.join(tables[i])
        chunks.append(chunk)
        
    return chunks