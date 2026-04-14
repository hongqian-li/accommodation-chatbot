# HAMK Accommodation Chatbot — Test Cases

**Project:** Privacy-Aware HAMK Student Accommodation Chatbot  
**Version:** 1.0  
**Test Date:** 2026-04-14  
**Tester:** Hongqian Li  
**Environment:** Local — Flask on `http://localhost:5000`, Ollama `llama3.2`, ChromaDB

---

## Test Scope

These test cases verify:
1. General accommodation queries are answered using the RAG knowledge base
2. Sensitive / GDPR Article 9 queries are blocked and redirected to email
3. The two-stage privacy classifier (keyword scan → LLM) works correctly
4. The chat UI displays both response types appropriately

---

## Test Cases

---

### TC-01 — General Query: Room search (open-ended)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-01 |
| **Category** | General Query |
| **Classification Stage** | Stage 2 (LLM) |
| **Screenshot** | `test_case_01_general_queries.jpeg` |

**Input message:**
> Hi, can you help me find a room?

**Expected result:**
- Classified as `general`
- RAG retrieves relevant chunks about room types
- Ollama generates a helpful response listing available room types at HAMK campuses
- Response is displayed in a standard grey bubble in the UI

**Actual result:**
- Classified as `general` ✅
- Bot responded with an overview of on-campus housing at Evo and Mustiala (shared apartments, studio/one-bedroom), mentioning basic furnishings and suggesting further options ✅
- Standard grey bubble displayed ✅

**Status: PASS**

---

### TC-02 — General Query: Location-specific accommodation search

| Field | Detail |
|---|---|
| **Test Case ID** | TC-02 |
| **Category** | General Query |
| **Classification Stage** | Stage 2 (LLM) |
| **Screenshot** | `test_case_01_general_queries.jpeg` |

**Input message:**
> How do I find accommodation in Hämeenlinna?

**Expected result:**
- Classified as `general`
- RAG retrieves relevant chunks about Hämeenlinna housing options
- Bot responds with information about HOPS, private rental platforms (Vuokraovi, Oikotie, NAL, Lumo, Joo-kodit), and Hämeenlinnan Asunnot for families
- No sensitive data processing occurs

**Actual result:**
- Classified as `general` ✅
- Bot correctly mentioned the Accommodation Coordinator, `arrival@hamk.fi`, HOPS, private rental platforms, and Hämeenlinnan Asunnot for family housing ✅
- Response shown in grey bubble ✅

**Status: PASS**

---

### TC-03 — Sensitive Query: Health condition (keyword match)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-03 |
| **Category** | Sensitive Query — GDPR Art. 9 Health Data |
| **Classification Stage** | Stage 1 (Keyword scan) |
| **Triggered keyword** | `chronic` / `illness` |
| **Screenshot** | `test_case_02_sensitive_and_general_queries.jpeg` |

**Input message:**
> I have a chronic illness and need a ground floor room.

**Expected result:**
- Stage 1 keyword scan detects `chronic` or `illness` (GDPR Art. 9 — health category)
- Classified as `sensitive` immediately, no LLM call made
- Response redirects user to `arrival@hamk.fi`
- Response is displayed with amber/yellow highlighted bubble in the UI
- Personal health data is never sent to the LLM

**Actual result:**
- Stage 1 keyword scan detected health keyword ✅
- Bot responded: *"Your question seems to involve personal or sensitive information. For privacy reasons, I'm not able to process that here. Please contact the HAMK accommodation team directly at arrival@hamk.fi — they will be happy to help you confidentially."* ✅
- Amber highlighted bubble displayed in UI ✅
- No LLM processing of health data ✅

**Status: PASS**

---

### TC-04 — Sensitive Query: Pregnancy / family situation (keyword match)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-04 |
| **Category** | Sensitive Query — GDPR Art. 9 Family Situation |
| **Classification Stage** | Stage 1 (Keyword scan) |
| **Triggered keyword** | `pregnant` |
| **Screenshot** | `test_case_03_sensitive_and_general_queries.jpeg` |

**Input message:**
> I am pregnant, do I qualify for family housing?

**Expected result:**
- Stage 1 keyword scan detects `pregnant` (GDPR Art. 9 — family situation category)
- Classified as `sensitive` immediately
- Redirect response shown, no LLM involvement
- Amber highlighted bubble in the UI

**Actual result:**
- Stage 1 keyword scan detected `pregnant` ✅
- Bot responded with the standard privacy redirect to `arrival@hamk.fi` ✅
- Amber highlighted bubble displayed ✅

**Status: PASS**

---

### TC-05 — General Query: Campus-specific housing search

| Field | Detail |
|---|---|
| **Test Case ID** | TC-05 |
| **Category** | General Query |
| **Classification Stage** | Stage 2 (LLM) |
| **Screenshot** | `test_case_03_sensitive_and_general_queries.jpeg` |

**Input message:**
> Is there housing near the Riihimäki campus?

**Expected result:**
- Classified as `general`
- RAG retrieves relevant chunks about Riihimäki housing
- Bot responds with information about HOPS Peltosaari apartments

**Actual result:**
- Classified as `general` ✅
- Bot responded: *"Yes, the Peltosaari area with apartments through HOPS is located near the Riihimäki Campus."* ✅
- Correct and concise answer grounded in the knowledge base ✅

**Status: PASS**

---

## Test Summary

| TC ID | Input Message | Type | Stage | Status |
|---|---|---|---|---|
| TC-01 | "Hi, can you help me find a room?" | General | 2 (LLM) | PASS |
| TC-02 | "How do I find accommodation in Hämeenlinna?" | General | 2 (LLM) | PASS |
| TC-03 | "I have a chronic illness and need a ground floor room." | Sensitive | 1 (Keyword) | PASS |
| TC-04 | "I am pregnant, do I qualify for family housing?" | Sensitive | 1 (Keyword) | PASS |
| TC-05 | "Is there housing near the Riihimäki campus?" | General | 2 (LLM) | PASS |

**Total: 5 / 5 PASS**

---

## Notes

- **TC-01 / TC-02 regression:** An earlier version of the app incorrectly classified general Hämeenlinna queries as sensitive due to: (1) the wrong Ollama model name (`llama3` instead of `llama3.2`), (2) substring keyword matching (`"ill"` firing inside `"still"`), and (3) an overly vague LLM classification prompt. All three were fixed before these test cases were recorded.
- **Sensitive response UI:** Amber-highlighted bubble with left border is shown for all sensitive responses to make the privacy redirect visually distinct from normal answers.
- **Privacy guarantee:** In TC-03 and TC-04, the user's health and family situation data never reaches the Ollama LLM — the keyword scan fires in Stage 1 before any LLM call is made.
