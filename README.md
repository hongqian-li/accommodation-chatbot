# HAMK Student Accommodation Chatbot

A privacy-aware AI chatbot that answers student accommodation questions for HAMK University of Applied Sciences — built as a hands-on learning project using Claude Code in a Cursor environment.

---

## What This Project Is

HAMK students — especially incoming international students — often have a lot of questions about finding accommodation: which campus has on-site housing, how much does a room cost, how do you apply, who do you contact. At the same time, accommodation queries can sometimes cross into sensitive personal territory (health conditions, pregnancy, financial hardship, legal status), which under GDPR Article 9 must never be processed by an AI system without explicit consent and safeguards.

This chatbot tries to solve both problems at once:

- Answer common accommodation questions accurately using a RAG (Retrieval-Augmented Generation) pipeline built on real HAMK accommodation data
- Detect and block GDPR Article 9 sensitive queries before they ever reach the LLM, redirecting the user to a human contact instead

Everything runs locally — no cloud APIs, no data leaving the machine.

---

## The Honest Story Behind This Project

I am a final-year student at HAMK, and student accommodation is actually the topic of my ongoing thesis. I have spent months building up research and knowledge in this area — understanding the housing landscape, the student pain points, the privacy concerns, and the information gaps.

My original intention was to build this tool myself from scratch. I wanted it to be mine. But I was also in the middle of learning about agentic AI and specifically **Claude Code**, which is a CLI-based AI coding agent. I decided to use my own thesis topic as the hands-on playground for that learning — a real project, with real domain knowledge I already had, built using a tool I was trying to understand.

The result is that this app was built almost entirely through a conversation with Claude Code running inside Cursor. I described what I wanted, directed the architecture, corrected mistakes, and made decisions — but the code was written by the agent. That is the experiment. And it worked faster than I expected.

---

## How It Was Built — Agentic AI Workflow

The entire project was built in a single session using **Claude Code** (Anthropic's CLI agent) running inside the **Cursor** IDE. The workflow was purely conversational — no manual file editing, no copy-pasting from Stack Overflow, no writing code independently.

Here is roughly how the session went:

| Step | What I asked | What Claude Code did |
|---|---|---|
| 1 | Initialise a git repo and create a `.gitignore` | Created `.gitignore`, ran `git init`, made first commit |
| 2 | Create a HAMK accommodation knowledge base | Fetched content from `hamk.fi`, wrote `hamk_accommodation.txt` with 6 structured sections |
| 3 | Build a RAG ingestion pipeline | Wrote `knowledge_base/ingest.py` — reads, chunks (300 chars / 50 overlap), embeds into ChromaDB |
| 4 | Build a RAG query module | Wrote `knowledge_base/query.py` — retrieves top-3 chunks for a query |
| 5 | Build a GDPR privacy classifier | Fetched GDPR Article 9 spec online, wrote `privacy_layer/keywords.py` (100+ keywords across 9 categories) and `privacy_layer/classifier.py` (two-stage: keyword scan + LLM fallback) |
| 6 | Build the Flask backend and chat UI | Wrote `app.py` (full request pipeline) and `templates/index.html` (chat UI with typing indicator, sensitive message highlighting) |
| 7 | Run the app and debug a false positive | Diagnosed that general queries were being flagged as sensitive — traced it to 3 bugs (wrong model name, substring keyword matching, vague LLM prompt) and fixed all three |
| 8 | Write test cases | Read screenshots I had taken, wrote 5 structured test cases in `test_cases/test_cases.md` |
| 9 | Write this README | Here we are |

Each step was a short natural-language instruction. Claude Code handled file creation, web fetching, git commits, debugging, and even process management (finding and killing stale Flask processes when multiple instances piled up).

---

## Architecture

```
User message
     │
     ▼
┌─────────────────────────────┐
│     Privacy Layer           │
│  Stage 1: Keyword scan      │  ──► SENSITIVE → Redirect to arrival@hamk.fi
│  Stage 2: LLM classify      │
└─────────────────────────────┘
     │ GENERAL
     ▼
┌─────────────────────────────┐
│     RAG Pipeline            │
│  ChromaDB vector search     │  ──► Top-3 relevant chunks
│  knowledge_base/query.py    │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│     LLM Answer Generation   │
│  Ollama (llama3.2, local)   │  ──► Answer grounded in HAMK data
│  llm/ollama_client.py       │
└─────────────────────────────┘
     │
     ▼
  Flask response → Chat UI
```

### Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| LLM | Ollama (`llama3.2`, runs locally) |
| Vector store | ChromaDB (persisted to `./chroma_db`) |
| Privacy classification | Keyword regex + Ollama LLM |
| Frontend | Plain HTML/CSS/JS (single page, served by Flask) |
| Knowledge base | Custom `.txt` file based on `hamk.fi` accommodation content |

---

## Project Structure

```
accommodation-chatbot/
├── app.py                        # Flask entry point — full request pipeline
├── requirements.txt
├── CLAUDE.md                     # Project context file for the AI agent
├── knowledge_base/
│   ├── ingest.py                 # Chunk, embed, and store docs in ChromaDB
│   ├── query.py                  # Retrieve top-3 relevant chunks
│   └── data/
│       └── hamk_accommodation.txt  # HAMK accommodation knowledge base
├── privacy_layer/
│   ├── keywords.py               # GDPR Art. 9 keyword list (9 categories, 100+ terms)
│   └── classifier.py             # Two-stage privacy classifier
├── llm/
│   └── ollama_client.py          # Ollama API wrapper
├── templates/
│   └── index.html                # Chat UI
├── test_cases/
│   └── test_cases.md             # 5 documented manual test cases
└── test_cases_screenshots/       # UI screenshots from test session
```

---

## Running the App

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com) installed

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Pull the model (first time only)
ollama pull llama3.2

# 3. Start Ollama
ollama serve

# 4. Ingest the knowledge base (first time only)
python knowledge_base/ingest.py

# 5. Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Key Learnings

### On agentic AI development

**It moves fast, but direction still matters.**
The agent wrote code quickly, but it could only go where I pointed it. Without a clear architecture in mind (from my thesis research), the prompts would have produced a mess. Domain knowledge still matters — the AI just removes the friction of translating that knowledge into working code.

**CLAUDE.md is underrated.**
Having a project context file that the agent reads at the start of each session kept the code consistent — naming conventions, file size limits, the privacy rules. It acts like a team spec document, except the entire "team" is one AI.

**Debugging is still a human job.**
The false-positive bug (general queries flagged as sensitive) required real diagnosis: checking which stage fired, reading Ollama API responses, tracing a substring match back to `"ill"` hiding inside `"still"`. The agent helped fix each individual issue once identified, but identifying them required understanding the system.

**Background processes pile up silently.**
When running a Flask app through an AI-managed session, each restart attempt spawned a new process without killing the old one. Six stale Flask instances were running simultaneously before we caught it. Not a Claude Code problem specifically — just a lesson about stateful side effects in agentic workflows.

### On building privacy-aware AI

**Keyword scanning is fast but brittle.**
Whole-word boundary matching (`\b`) is essential — otherwise short keywords like `"ill"` match inside unrelated words. Start with regex word boundaries, not plain substring search.

**LLM-based classification needs examples, not just rules.**
A vague prompt ("flag GDPR Article 9 data") caused the LLM to over-flag everything. Adding a handful of concrete general examples ("How much does a room cost?" → general) fixed it immediately. Few-shot grounding in the domain is more effective than abstract instructions.

**Fail safe, not fail open.**
When the LLM is unavailable or returns something unexpected, the system defaults to `"sensitive"`. This is the right call for a privacy-critical layer — it is better to send one extra email than to accidentally process protected data.

### On using a thesis topic as a learning project

Using real domain knowledge as the foundation made the project more grounded and more honest. The knowledge base content, the privacy rules, and the test cases all came from months of thesis research — the AI just helped build the delivery mechanism around that knowledge. That felt like the right division of responsibility.

---

## Test Results

5 manual test cases documented in `test_cases/test_cases.md` — all passing.

| TC | Query | Expected | Result |
|---|---|---|---|
| TC-01 | "Hi, can you help me find a room?" | General answer | PASS |
| TC-02 | "How do I find accommodation in Hämeenlinna?" | General answer | PASS |
| TC-03 | "I have a chronic illness and need a ground floor room." | Sensitive redirect | PASS |
| TC-04 | "I am pregnant, do I qualify for family housing?" | Sensitive redirect | PASS |
| TC-05 | "Is there housing near the Riihimäki campus?" | General answer | PASS |

---

## Contact

For real HAMK accommodation enquiries: **arrival@hamk.fi**

---

*Built as a hands-on learning project for agentic AI development — HAMK University of Applied Sciences, 2026.*
