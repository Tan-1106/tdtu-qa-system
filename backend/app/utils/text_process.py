import re
import json
import fitz

# Utility functions for document upload and processing
# Check if a PDF is text-based
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

# Normalize table cell content
def normalize_text(text: str):
    if isinstance(text, str):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            try:
                import ast
                data = ast.literal_eval(text)
            except Exception:
                data = [text]
    else:
        data = text

    if isinstance(data, list):
        cleaned = []
        for item in data:
            if isinstance(item, str):
                s = item.replace("\n", " ")
                s = re.sub(r"\s+", " ", s).strip()
                cleaned.append(s)
        return cleaned

    if isinstance(data, str):
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    return data

# Clean individual table cell content
def clean_cell(x):
    x = str(x)
    x = re.sub(r'[\n\r\t]+', '', x)
    x = re.sub(r'\s{2,}', ' ', x)
    return x.strip()

# Split text into chunks
async def split_text_into_chunks(text: str, words_per_chunk: int = 800, overlap: int = 300) -> list[str]:
    text = text.strip()
    chunks = []
    
    words = text.split()
    for i in range(0, len(words), words_per_chunk - overlap):
        chunk = " ".join(words[i:i + words_per_chunk])
        if len(chunk.split()) > 30:
            chunks.append(chunk)

    return chunks