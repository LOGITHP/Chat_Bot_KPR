import fitz  # PyMuPDF
from typing import List
from app.documents.base import BaseParser, DocumentChunk
from app.config import settings

class PDFParser(BaseParser):
    def parse(self, file_path: str) -> List[DocumentChunk]:
        chunks = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    # Very basic chunking per page. Complex section chunking could be added here.
                    chunks.append(DocumentChunk(
                        text=text.strip(),
                        page=page_num + 1
                    ))
            return chunks
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return []
