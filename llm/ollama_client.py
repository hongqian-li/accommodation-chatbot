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
student accommodation queries. Answer using the provided context below.
If the context includes a WEB SEARCH RESULTS section, summarise those results
directly — include the listing counts, URLs, and any specific details shown.
If the answer is not in the context, say you don't have that information and
suggest the student contact arrival@hamk.fi for further help.
Be concise, friendly, and factual. Do not ask for or repeat any personal information."""


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
