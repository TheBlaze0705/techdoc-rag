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

d all of these at once. The current version is intentionally simple enough to understand.
