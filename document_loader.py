import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
import config

def load_text_file(filepath: Path) -> str:
    """Reads content from plain text or markdown files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[Warning] Failed to read {filepath}: {e}")
        return ""

def load_pdf_file(filepath: Path) -> str:
    """Extracts text content from a PDF file using PyPDF."""
    text = ""
    try:
        reader = PdfReader(str(filepath))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_idx + 1} ---\n" + page_text
    except Exception as e:
        print(f"[Warning] Failed to extract text from PDF {filepath}: {e}")
    return text

def load_documents(data_dir: Path = config.DATA_DIR) -> List[Dict[str, Any]]:
    """Recursively loads all documents from the data directory."""
    documents = []
    if not data_dir.exists():
        print(f"[Warning] Data directory '{data_dir}' does not exist.")
        return documents

    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            content = ""
            if ext in [".txt", ".md", ".json", ".csv"]:
                content = load_text_file(file_path)
            elif ext == ".pdf":
                content = load_pdf_file(file_path)

            if content.strip():
                # Relative path for cleaner metadata
                rel_path = file_path.relative_to(data_dir.parent).as_posix()
                documents.append({
                    "source": rel_path,
                    "filename": file_path.name,
                    "content": content
                })

    print(f"[Loader] Loaded {len(documents)} document(s) from {data_dir}")
    return documents

def split_text_into_chunks(text: str, chunk_size: int = config.CHUNK_SIZE, chunk_overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """Splits a body of text into sliding window chunks with overlap."""
    if not text:
        return []
    
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    step = chunk_size - chunk_overlap
    if step <= 0:
        step = chunk_size

    while start < len(words):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        start += step

    return chunks

def process_documents_for_indexing() -> List[Dict[str, Any]]:
    """Loads and chunks all documents, returning chunk records with metadata."""
    raw_docs = load_documents()
    chunked_records = []

    for doc in raw_docs:
        chunks = split_text_into_chunks(doc["content"])
        for idx, chunk_text in enumerate(chunks):
            chunked_records.append({
                "chunk_id": f"{doc['filename']}_chunk_{idx}",
                "text": chunk_text,
                "source": doc["source"],
                "filename": doc["filename"],
                "chunk_index": idx
            })

    print(f"[Loader] Total chunks generated: {len(chunked_records)}")
    return chunked_records

if __name__ == "__main__":
    records = process_documents_for_indexing()
    for r in records[:3]:
        print("Sample Chunk:", r)
