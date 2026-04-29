from pathlib import Path
import pandas as pd
from pypdf import PdfReader
from docx import Document as DocxDocument
import tempfile
import os
from app.core.s3_client import S3Client

async def parse_file(path: str) -> str:
    # Check if path is S3 URL
    if path.startswith("https://") and ".s3." in path:
        # Extract bucket and key from S3 URL
        # URL format: https://bucket-name.s3.region.amazonaws.com/key
        url_parts = path.replace("https://", "").split("/")
        bucket = url_parts[0].split(".s3.")[0]
        key = "/".join(url_parts[1:])
        
        s3_client = S3Client()
        file_content = await s3_client.download_file(key)
        
        # Create temporary file
        suffix = Path(key).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            return await _parse_file_content(temp_path)
        finally:
            os.unlink(temp_path)
    else:
        # Local file path
        return await _parse_file_content(path)

async def _parse_file_content(path: str) -> str:
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
