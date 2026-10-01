from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .llm import generate_with_ollama
from .parser import chunk_text, extract_text


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class RAGEngine:
    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_path = index_dir / "vectors.faiss"
        self.metadata_path = index_dir / "metadata.json"

        self.model = SentenceTransformer(MODEL_NAME)
        self.dimension = self.model.get_sentence_embedding_dimension()

        self.index = None
        self.metadata: list[dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        else:
            # Inner product + normalized vectors = cosine similarity.
            self.index = faiss.IndexFlatIP(self.dimension)

    def _save(self):
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(self.metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _embed_documents(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype("float32")

    def _embed_query(self, question: str) -> np.ndarray:
        vector = self.model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vector.astype("float32")

    def add_document(self, path: Path) -> int:
        records = extract_text(path)

        new_metadata = []
        texts = []

        chunk_id = len(self.metadata)

        for record in records:
            chunks = chunk_text(
                record["text"],
                chunk_size=int(os.getenv("CHUNK_SIZE", "900")),
                overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
            )

            for chunk in chunks:
                texts.append(chunk)
                new_metadata.append({
                    "chunk_id": chunk_id,
                    "filename": path.name,
                    "page": record["page"],
                    "text": chunk,
                })
                chunk_id += 1

        if not texts:
            raise ValueError("No readable text was found in the document.")

        vectors = self._embed_documents(texts)
        self.index.add(vectors)
        self.metadata.extend(new_metadata)
        self._save()

        return len(texts)

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        if not self.metadata or self.index.ntotal == 0:
            return []

        query_vector = self._embed_query(question)
        k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, index_id in zip(scores[0], indices[0]):
            if index_id < 0:
                continue

            item = dict(self.metadata[index_id])
            item["similarity"] = float(score)
            results.append(item)

        return results

    def ask(self, question: str, top_k: int = 5) -> dict:
        results = self.search(question, top_k)

        if not results:
            return {
                "question": question,
                "answer": "No documents have been indexed yet. Upload a PDF, Markdown, or TXT file first.",
                "grounded": False,
                "confidence": 0.0,
                "sources": [],
                "note": "No searchable documentation is available.",
            }

        # This is the "anti-hallucination" feature.
        # A low score means the question is probably outside the uploaded docs.
        threshold = float(os.getenv("MIN_SIMILARITY", "0.35"))
        best_score = results[0]["similarity"]
        grounded = best_score >= threshold

        sources = [
            {
                "filename": r["filename"],
                "page": r["page"],
                "chunk_id": r["chunk_id"],
                "similarity": round(max(0.0, min(1.0, r["similarity"])), 4),
                "text": r["text"],
            }
            for r in results
        ]

        if not grounded:
            return {
                "question": question,
                "answer": (
                    "I couldn't find strong enough evidence for this question "
                    "in the uploaded documentation. Try asking about a topic "
                    "that appears in the documents."
                ),
                "grounded": False,
                "confidence": round(max(0.0, best_score), 4),
                "sources": sources,
                "note": "Low semantic similarity: answer generation was blocked.",
            }

        context = "\n\n".join(
            f"[Source {i+1} | {r['filename']} | page {r['page'] or 'N/A'}]\n{r['text']}"
            for i, r in enumerate(results)
        )

        # Optional generative RAG. If Ollama isn't installed/running,
        # the system still works using a simple extractive response.
        answer = generate_with_ollama(question, context)

        if not answer:
            answer = (
                "Based on the most relevant documentation sections:\n\n"
                + "\n\n".join(
                    f"• {r['text']}" for r in results[:3]
                )
            )
            note = (
                "Extractive mode: Ollama was not available. "
                "The answer below is taken directly from retrieved documentation."
            )
        else:
            note = "Generative mode: the local LLM answered using only the retrieved chunks."

        return {
            "question": question,
            "answer": answer,
            "grounded": True,
            "confidence": round(max(0.0, min(1.0, best_score)), 4),
            "sources": sources,
            "note": note,
        }

    def documents(self) -> list[str]:
        return sorted(set(item["filename"] for item in self.metadata))

    def document_count(self) -> int:
        return len(self.documents())

    def chunk_count(self) -> int:
        return len(self.metadata)
