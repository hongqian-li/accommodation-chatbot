"""
Ollama API wrapper for generating answers using RAG context.

Reads OLLAMA_URL and OLLAMA_MODEL from environment variables,
with sensible defaults for local development.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = """You are a helpful assistant for HAMK University of Applied Sciences
student accommodation queries.

Rules for answering:
1. Read the Knowledge Base context first. If it clearly answers the question,
   give that answer and STOP — do not add web results.
2. Only turn to the WEB SEARCH RESULTS if the Knowledge Base does not contain
   the answer. When using web results, include counts, URLs, and details.
3. Never mix KB answers with unrelated web results.
4. If neither source has the answer, say so and suggest arrival@hamk.fi.
5. Be concise, friendly, and factual."""


def generate_answer(query: str, context: str) -> str:
    """
    Generate an answer to a student query using retrieved RAG context.

    Args:
        query:   The student's question.
        context: RAG chunks from ChromaDB, optionally followed by a
                 'WEB SEARCH RESULTS' section when the query needed
                 live data.

    Returns:
        The model's answer as a plain string.

    Raises:
        requests.exceptions.ConnectionError: If Ollama is not running.
        requests.exceptions.HTTPError: If the Ollama API returns an error.
    """
    has_web = "===WEB SEARCH RESULTS" in context
    web_instruction = (
        "\nIMPORTANT: The context contains live WEB SEARCH RESULTS. "
        "Use them to answer — include listing counts and direct URLs where available.\n"
        if has_web else ""
    )
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"{web_instruction}"
        f"Student question: {query}\n\n"
        f"Answer:"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "").strip()


def is_ollama_running() -> bool:
    """
    Check whether the Ollama service is reachable.

    Returns:
        True if Ollama responds, False otherwise.
    """
    base_url = OLLAMA_URL.rsplit("/api/", 1)[0]
    try:
        requests.get(base_url, timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False
