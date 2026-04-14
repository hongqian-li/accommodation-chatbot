"""
Privacy classifier for GDPR Article 9 compliance.

Two-stage classification:
  Stage 1 — Fast keyword scan using SENSITIVE_KEYWORDS list.
             If a match is found, immediately return "sensitive".
  Stage 2 — If no keyword match, call Ollama (llama3) for LLM-based
             classification. Returns "sensitive" or "general".
"""

import json
import requests
from privacy_layer.keywords import get_matched_keywords, get_matched_categories

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

CLASSIFICATION_PROMPT = """You are a GDPR Article 9 privacy filter for a university student accommodation chatbot.

Your ONLY job is to decide if a message contains GDPR Article 9 special category data.
Most accommodation questions are GENERAL. Only flag as SENSITIVE if the message explicitly
reveals or requests processing of: health/medical conditions, disability, racial or ethnic
origin, political opinions, religious beliefs, sexual orientation, genetic/biometric data,
criminal convictions, or clear financial hardship (debt, bankruptcy).

GENERAL examples (answer general):
- "How do I find accommodation in Hämeenlinna?"
- "What rooms are available at Evo campus?"
- "How much does a room cost at Lepaa?"
- "How do I apply for student housing?"
- "Is there housing near the Riihimäki campus?"
- "What is the application deadline?"
- "Hi, can you help me find a room?"

SENSITIVE examples (answer sensitive):
- "I have a chronic illness and need a ground floor room."
- "I am pregnant, do I qualify for family housing?"
- "I was declared bankrupt, can I still apply?"
- "I am an asylum seeker, am I eligible?"
- "I have depression and need a quiet room."

Respond with ONLY a JSON object — no extra text, no markdown:
{{"result": "sensitive" or "general", "reason": "one sentence explanation"}}

User message: "{message}"
"""


def _call_ollama(message: str) -> dict:
    """Call Ollama llama3 to classify a message. Returns parsed JSON dict."""
    prompt = CLASSIFICATION_PROMPT.format(message=message)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    response.raise_for_status()

    raw = response.json().get("response", "").strip()

    # Extract JSON block in case the model adds surrounding text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in Ollama response: {raw!r}")

    return json.loads(raw[start:end])


def classify(message: str) -> dict:
    """
    Classify a user message for GDPR Article 9 sensitivity.

    Returns:
        {
            "result": "sensitive" | "general",
            "stage": 1 | 2,
            "reason": "brief explanation"
        }
    """
    # ------------------------------------------------------------------
    # Stage 1: Keyword scan
    # ------------------------------------------------------------------
    matched_keywords = get_matched_keywords(message)
    if matched_keywords:
        matched_categories = get_matched_categories(message)
        categories_str = ", ".join(matched_categories)
        keywords_str = ", ".join(matched_keywords[:5])  # show up to 5
        return {
            "result": "sensitive",
            "stage": 1,
            "reason": (
                f"Keyword match detected — '{keywords_str}' "
                f"(GDPR Art. 9 categories: {categories_str})."
            ),
        }

    # ------------------------------------------------------------------
    # Stage 2: LLM classification via Ollama
    # ------------------------------------------------------------------
    try:
        llm_response = _call_ollama(message)
        result = llm_response.get("result", "general").strip().lower()
        reason = llm_response.get("reason", "LLM classification.")

        if result not in ("sensitive", "general"):
            result = "general"
            reason = "LLM returned unexpected value; defaulting to general."

        return {
            "result": result,
            "stage": 2,
            "reason": reason,
        }

    except requests.exceptions.ConnectionError:
        return {
            "result": "sensitive",
            "stage": 2,
            "reason": (
                "Ollama service unavailable. Defaulting to sensitive "
                "to preserve GDPR compliance."
            ),
        }
    except Exception as e:
        return {
            "result": "sensitive",
            "stage": 2,
            "reason": f"LLM classification failed ({e}). Defaulting to sensitive.",
        }


if __name__ == "__main__":
    test_messages = [
        "I have a disability and need an accessible room.",
        "What is the rent at Lepaa campus?",
        "I am pregnant and looking for family accommodation.",
        "I was recently declared bankrupt and need affordable housing.",
        "How do I apply for a room at Mustiala?",
        "I am an asylum seeker. Can I apply for student housing?",
    ]

    print(f"{'Message':<55} {'Result':<10} {'Stage':<7} Reason")
    print("-" * 120)
    for msg in test_messages:
        r = classify(msg)
        print(f"{msg[:54]:<55} {r['result']:<10} {r['stage']:<7} {r['reason']}")
