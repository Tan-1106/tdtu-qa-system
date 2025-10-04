import re
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
def normalize_cell(cell: str) -> str:
    if not isinstance(cell, str):
        return cell
    text = cell.replace("\n", "")
    text = text.replace("\\", "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()