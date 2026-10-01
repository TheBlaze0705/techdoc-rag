import os
import requests


def generate_with_ollama(question: str, context: str) -> str | None:
    """
    Optional local answer generation.

    If Ollama isn't running, return None and the RAG engine will
    use an extractive answer instead.
    """
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    prompt = f"""
You are a technical documentation assistant.

Answer the user's question using ONLY the supplied documentation context.
If the context does not contain enough information, say:
"I don't have enough information in the uploaded documentation."

Do not invent commands, APIs, versions, configuration values, or facts.
Keep the answer clear for a third-year computer science student.
Use short bullets when useful.

USER QUESTION:
{question}

DOCUMENTATION CONTEXT:
{context}
""".strip()

    try:
        response = requests.post(
            f"{url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip() or None
    except Exception:
        return None
