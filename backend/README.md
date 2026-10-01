# TechDoc RAG — Backend

## What this backend does

1. Accepts `.pdf`, `.md`, `.txt`
2. Extracts text
3. Splits text into overlapping chunks
4. Converts chunks into embeddings using `all-MiniLM-L6-v2`
5. Stores normalized vectors in FAISS
6. Converts a user question into an embedding
7. Retrieves the top-k chunks using cosine similarity
8. Blocks weak matches using a similarity threshold
9. Generates a grounded answer with optional local Ollama
10. Returns source chunks so the UI can show where the answer came from

## Run

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API:
- http://localhost:8000/docs
- GET `/api/health`
- GET `/api/documents`
- POST `/api/upload`
- POST `/api/ask`

## Optional: local LLM

Install Ollama, then:

```bash
ollama pull llama3.2:3b
ollama serve
```

If Ollama isn't running, the project automatically uses extractive mode, so you can still demonstrate the RAG pipeline without an API key.
