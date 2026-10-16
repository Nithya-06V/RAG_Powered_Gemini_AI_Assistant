from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".csv"}


def extract_pages(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(str(path))
        pages = [
            {"text": page.extract_text() or "", "page": page_number}
            for page_number, page in enumerate(reader.pages, start=1)
        ]
    elif extension == ".docx":
        document = Document(str(path))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        pages = [{"text": text, "page": None}]
    elif extension == ".csv":
        table = pd.read_csv(path).fillna("")
        pages = [{"text": table.to_string(index=False), "page": None}]
    elif extension in {".txt", ".md"}:
        pages = [{"text": path.read_text(encoding="utf-8-sig"), "page": None}]
    else:
        raise ValueError("Unsupported file type. Upload PDF, TXT, MD, DOCX, or CSV.")

    if not any(page["text"].strip() for page in pages):
        raise ValueError("No readable text was found in this document.")
    return pages


def split_pages(pages, chunk_size=1200, overlap=180):
    chunks = []
    for page in pages:
        text = " ".join(page["text"].split())
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append({"text": chunk, "page": page["page"]})
            if end == len(text):
                break
            start = end - overlap
    return chunks
