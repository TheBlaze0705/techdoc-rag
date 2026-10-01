from typing import List
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=10)


class Source(BaseModel):
    filename: str
    page: int | None = None
    chunk_id: int
    similarity: float
    text: str


class AskResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    confidence: float
    sources: List[Source]
    note: str


class UploadResponse(BaseModel):
    message: str
    files: list
