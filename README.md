# TechDoc RAG — Full-Stack RAG Project

A Retrieval-Augmented Generation (RAG) system for technical documentation.

## Main idea

```text
             DOCUMENT INGESTION
PDF / MD / TXT
       |
       v
Text Extraction
       |
       v
Chunking
       |
       v
Sentence Transformer
       |
       v
Vector Embeddings
       |
       v
FAISS Vector Store
       |
       |                    USER QUESTION
       |                         |
       |                         v
       |                  Question Embedding
       |                         |
       +-----------> Cosine Similarity
                                 |
                                 v
                              Top-K
                                 |
                                 v
                         Confidence Gate
                          /            \
                       enough          weak
                         |              |
                         v              v
                    LLM answer     "Not enough
                    + sources       evidence"
```

## What makes it different from a basic RAG demo?

### 1. Confidence gate
The system does not blindly generate an answer. It first checks the best cosine similarity score. If the question is poorly supported by the uploaded documents, answer generation is blocked.

### 2. Evidence explorer
Every answer returns the exact retrieved chunks, filename, page number (for PDFs), and similarity score. This makes the project easy to demonstrate.

### 3. Optional local LLM
You can run Ollama locally. If you don't, the system still works in extractive mode, which is useful for understanding the RAG pipeline before learning LLM APIs.

## Technology

### Backend
- Python
- FastAPI
- Sentence Transformers
- FAISS
- PyMuPDF
- NumPy
- Optional Ollama

### Frontend
- React
- Vite
- CSS

## Setup

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://localhost:8000

Swagger API docs: http://localhost:8000/docs

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally:

http://localhost:5173

## Optional LLM

Install Ollama and pull a small model:

```bash
ollama pull llama3.2:3b
ollama serve
```

The backend calls:

```text
POST http://localhost:11434/api/generate
```

If it is unavailable, the project automatically falls back to extractive answers.

## Good documents to test

Use public technical documentation such as:
- Python documentation
- Git documentation
- Docker documentation
- React documentation
- FastAPI documentation
- AWS service documentation

Start with a small document first.

## Important RAG concepts

### Chunking
Large documents are divided into smaller pieces because embedding an entire 100-page document as one vector makes retrieval less precise.

### Embeddings
An embedding converts text into a numerical vector representing its semantic meaning.

### Cosine similarity
We compare the question vector with document vectors. A higher cosine similarity means the vectors point in more similar directions.

### Top-K
Instead of sending the whole database to the LLM, we retrieve only the K most relevant chunks.

### Grounding
The answer is generated from retrieved documentation rather than from the model's general memory.

## Why FAISS works for cosine similarity

The project normalizes all embeddings and uses FAISS `IndexFlatIP`.

For normalized vectors:

```text
cosine_similarity(a, b) = a · b
```

So maximum inner-product search becomes cosine-similarity search.

## Project structure

```text
techdoc-rag/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── rag.py
│   │   ├── parser.py
│   │   ├── llm.py
│   │   └── schemas.py
│   ├── data/
│   │   ├── uploads/
│   │   └── index/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md
```

## Suggested college-project extensions

Once the basic project works, add these one at a time:

1. Delete/re-index individual documents
2. Store document metadata in SQLite
3. Add authentication
4. Add chat history
5. Add document-specific filtering
6. Add hybrid search: BM25 + vector search
7. Add a cross-encoder reranker
8. Add OCR for scanned PDFs
9. Add streaming LLM responses
10. Add evaluation questions and retrieval-accuracy metrics

Don't add all of these at once. The current version is intentionally simple enough to understand.
