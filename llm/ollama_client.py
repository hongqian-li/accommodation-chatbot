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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

SYSTEM_PROMPT = """You are a helpful assistant for HAMK University of Applied Sciences
student accommodation queries. Answer only using the provided context.
If the answer is not in the context, say you don't have that information and
suggest the student contact arrival@hamk.fi for further help.
Be concise, friendly, and factual. Do not ask for or repeat any personal information."""


def generate_answer(query: str, context: str) -> str:
    """
    Generate an answer to a student query using retrieved RAG context.

    Args:
        query:   The student's question.
        context: Relevant text chunks retrieved from ChromaDB.

    Returns:
        The model's answer as a plain string.

    Raises:
        requests.exceptions.ConnectionError: If Ollama is not running.
        requests.exceptions.HTTPError: If the Ollama API returns an error.
    """
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
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
