from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .rag import RAGEngine
from .schemas import AskRequest, AskResponse, UploadResponse

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "index"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

engine = RAGEngine(INDEX_DIR)

app = FastAPI(
    title="TechDoc RAG API",
    description="Simple RAG system for PDF, Markdown and TXT technical documentation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "documents": engine.document_count(), "chunks": engine.chunk_count()}


@app.get("/api/documents")
def documents():
    return {"documents": engine.documents()}


@app.post("/api/upload", response_model=UploadResponse)
async def upload(files: List[UploadFile] = File(...)):
    accepted = {".pdf", ".md", ".txt"}
    uploaded = []

    for file in files:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in accepted:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename}: only PDF, MD and TXT files are supported."
            )

        content = await file.read()
        if not content:
            continue

        safe_name = Path(file.filename).name
        destination = UPLOAD_DIR / safe_name
        destination.write_bytes(content)

        try:
            count = engine.add_document(destination)
            uploaded.append({"filename": safe_name, "chunks_added": count})
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Could not process {safe_name}: {exc}")

    return {
        "message": f"Processed {len(uploaded)} document(s).",
        "files": uploaded
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return engine.ask(request.question, request.top_k)
