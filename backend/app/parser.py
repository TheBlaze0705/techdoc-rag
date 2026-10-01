from pathlib import Path
import pymupdf


def extract_text(path: Path) -> list[dict]:
    """
    Returns page/section-aware text.

    PDF -> one record per page.
    MD/TXT -> one record for the complete file.
    """
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        records = []
        with pymupdf.open(path) as doc:
            for page_number, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if text:
                    records.append({
                        "text": text,
                        "page": page_number,
                    })
        return records

    if suffix in {".md", ".txt"}:
        return [{
            "text": path.read_text(encoding="utf-8", errors="ignore"),
            "page": None,
        }]

    raise ValueError("Unsupported file type")


def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """
    Beginner-friendly character based chunker.
    It keeps a small overlap so context isn't abruptly lost.
    """
    text = clean_text(text)
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer ending at a sentence/space when possible.
        if end < len(text):
            boundary = max(
                text.rfind(". ", start, end),
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            )
            if boundary > start + chunk_size // 2:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks
