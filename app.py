"""
Flask entry point for the HAMK Privacy-Aware Accommodation Chatbot.

Logic flow per request:
  1. Receive user message
  2. Stage 1: keyword scan (privacy_layer.classifier)
  3. Stage 2 (if needed): LLM privacy classification via Ollama
  4. SENSITIVE  → return a redirect-to-email response (no LLM processing)
  5. GENERAL    → RAG retrieval from ChromaDB
                  If RAG confidence is low → web search fallback (DuckDuckGo)
                  → Ollama generates answer from combined context
"""

import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from privacy_layer.classifier import classify
from knowledge_base.query import get_context_with_confidence
from knowledge_base.web_search import search_finnish_housing, web_search
from llm.ollama_client import generate_answer, is_ollama_running

load_dotenv()

app = Flask(__name__)

SENSITIVE_RESPONSE = (
    "Your question seems to involve personal or sensitive information. "
    "For privacy reasons, I'm not able to process that here. "
    "Please contact the HAMK accommodation team directly at "
    "<a href='mailto:arrival@hamk.fi'>arrival@hamk.fi</a> — "
    "they will be happy to help you confidentially."
)

OLLAMA_UNAVAILABLE_RESPONSE = (
    "The AI service is currently unavailable. "
    "Please try again in a moment, or contact "
    "<a href='mailto:arrival@hamk.fi'>arrival@hamk.fi</a> for direct assistance."
)


@app.route("/")
def index():
    """Serve the main chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle a chat message from the user.

    Expects JSON body: {"message": "..."}
    Returns JSON: {"reply": "...", "sensitive": bool, "stage": int, "web_search_used": bool}
    """
    data = request.get_json(silent=True)
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "No message provided."}), 400

    message = data["message"].strip()

    # --- Privacy classification ---
    classification = classify(message)
    is_sensitive = classification["result"] == "sensitive"

    if is_sensitive:
        return jsonify({
            "reply": SENSITIVE_RESPONSE,
            "sensitive": True,
            "stage": classification["stage"],
        })

    # --- RAG retrieval + answer generation ---
    if not is_ollama_running():
        return jsonify({
            "reply": OLLAMA_UNAVAILABLE_RESPONSE,
            "sensitive": False,
            "stage": classification["stage"],
        })

    web_used = False
    try:
        context, needs_web = get_context_with_confidence(message)
        if needs_web:
            # Try Finnish housing sites first; fall back to general web search
            web_results = search_finnish_housing(message) or web_search(message)
            if web_results:
                context = context + "\n\n---\n\nWEB SEARCH RESULTS:\n" + web_results
                web_used = True
        answer = generate_answer(message, context)
    except Exception as e:
        app.logger.error("Error generating answer: %s", e)
        return jsonify({
            "reply": OLLAMA_UNAVAILABLE_RESPONSE,
            "sensitive": False,
            "stage": classification["stage"],
        }), 500

    return jsonify({
        "reply": answer,
        "sensitive": False,
        "stage": classification["stage"],
        "web_search_used": web_used,
    })


@app.route("/health")
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "ollama": is_ollama_running(),
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
