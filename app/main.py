"""DocuMind AI public HTTP API."""
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.extractor import extract_fields, read_document
from app.schemas import DocumentResult

MAX_FILE_BYTES = 5 * 1024 * 1024  # Week 1 safety limit: 5 MiB
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

app = FastAPI(
    title="DocuMind AI",
    description="Extract text and basic structured fields from documents.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple operational health check."""
    return {"status": "ok"}


@app.post("/extract", response_model=DocumentResult)
async def extract(file: UploadFile = File(...)) -> DocumentResult:
    """Validate a small upload, extract its text, and return structured JSON."""
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only PDF and TXT files are supported")

    try:
        # Read at most limit + 1 bytes; never trust the client's Content-Length.
        data = await file.read(MAX_FILE_BYTES + 1)
    finally:
        await file.close()

    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Maximum file size is 5 MiB")
    if extension == ".pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File does not appear to be a PDF")

    try:
        text, page_count = read_document(data, extension)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return DocumentResult(
        filename=filename,
        document_type=extension.lstrip("."),
        character_count=len(text),
        page_count=page_count,
        text=text,
        fields=extract_fields(text),
    )
