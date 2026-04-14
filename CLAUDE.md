# CLAUDE.md — Project Context for AI Agent

## Project Overview
A privacy-aware AI chatbot for HAMK student accommodation queries.
Built as a hands-on learning project to demonstrate agentic AI-assisted development.

## Architecture
- **LLM**: Ollama (llama3) running locally
- **Knowledge Base**: ChromaDB with HAMK accommodation data
- **Privacy Layer**: Two-stage classification (keyword + LLM)
- **Backend**: Flask (Python)
- **Frontend**: Single HTML page served by Flask

## Project Structure
```
hamk-privacy-chatbot/
├── CLAUDE.md
├── requirements.txt
├── app.py                  # Flask entry point
├── knowledge_base/
│   ├── ingest.py           # Load docs into ChromaDB
│   ├── query.py            # RAG retrieval logic
│   └── data/
│       └── hamk_accommodation.txt
├── privacy_layer/
│   ├── classifier.py       # Two-stage privacy classification
│   └── keywords.py         # GDPR Article 9 keyword list
├── llm/
│   └── ollama_client.py    # Ollama API wrapper
└── templates/
    └── index.html          # Chat UI
```

## Core Logic Flow
1. User sends a message
2. Privacy Layer Stage 1: keyword scan (fast)
3. If uncertain → Privacy Layer Stage 2: LLM classification
4. If SENSITIVE → return redirect message (no LLM processing of personal data)
5. If GENERAL → RAG retrieval from ChromaDB → Ollama generates answer

## Privacy Classification Rules
- SENSITIVE queries: anything involving personal situation, family, health, relationship status, pregnancy, financial hardship, legal issues → redirect to email
- GENERAL queries: room types, prices, application process, deadlines, locations → answer from knowledge base
- GDPR Article 9 special category data must NEVER be processed by the LLM

## Coding Conventions
- Python 3.10+
- All functions must have docstrings
- Environment variables via python-dotenv (.env file)
- No API keys or personal data in code
- Keep each file under 150 lines — split if needed
- Always test after each phase before moving to the next

## Key Commands
```bash
# Start Ollama
ollama serve

# Pull model (first time only)
ollama pull llama3

# Ingest knowledge base
python knowledge_base/ingest.py

# Run app
python app.py
```

## Do Not
- Do not process sensitive personal data through the LLM
- Do not store conversation history to disk
- Do not add unnecessary dependencies
- Do not over-engineer — keep it simple and working
