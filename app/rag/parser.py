from pathlib import Path
import pandas as pd
from pypdf import PdfReader
from docx import Document as DocxDocument

async def parse_file(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = DocxDocument(str(p))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    if suffix in {".txt", ".md"}:
        return p.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".csv":
        df = pd.read_csv(p)
        return df.to_csv(index=False)
    raise ValueError(f"Unsupported file type: {suffix}")
