# HAMK Accommodation Chatbot — Test Cases

**Project:** Privacy-Aware HAMK Student Accommodation Chatbot  
**Version:** 1.1  
**Test Date:** 2026-04-14  
**Tester:** Hongqian Li  
**Environment:** Local — Flask on `http://localhost:5000`, Ollama `llama3.2`, ChromaDB

---

## Test Scope

These test cases verify:
1. General accommodation queries are answered using the RAG knowledge base
2. Sensitive / GDPR Article 9 queries are blocked and redirected to email
3. The two-stage privacy classifier (keyword scan → LLM) works correctly
4. Live intent queries trigger web search and return real listing results
5. Non-housing queries (e.g. transport) route to general web search, not Finnish housing sites
6. The chat UI displays both response types appropriately

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
- Bot responded with the standard privacy redirect to `arrival@hamk.fi` ✅
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

### TC-06 — Web Search: Live listings on Vuokraovi (live intent)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-06 |
| **Category** | General Query — Web Search (Live Intent) |
| **Classification Stage** | Stage 2 (LLM) |
| **Web search triggered** | Yes — `_has_live_intent()` matched "can you search" |
| **Screenshot** | `test_case_04.jpeg` |

**Input message:**
> Can you search Hämeenlinna apartments on Vuokraovi for me?

**Expected result:**
- Classified as `general`
- Live intent keyword detected ("can you search") → web search forced regardless of RAG distance
- `search_finnish_housing()` queries Vuokraovi/Oikotie/HOPS
- Response includes listing counts and direct URLs

**Actual result:**
- Classified as `general` ✅
- Live intent detected, web search triggered ✅
- Bot returned: 245 apartments at `/vuokra-asunnot/hämeenlinna`, 190 at `/vuokra-asunnot/hämeenlinna/yksio`, 52 one-bedroom apartments — all with direct Vuokraovi URLs ✅
- `web_search_used: true` ✅

**Status: PASS**

---

### TC-07 — Web Search: Room near Riihimäki campus (live action intent)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-07 |
| **Category** | General Query — Web Search (Live Intent) |
| **Classification Stage** | Stage 2 (LLM) |
| **Web search triggered** | Yes — `_has_live_intent()` matched "find me" |
| **Screenshot** | `test_case_04.jpeg` |

**Input message:**
> Find me a room near Riihimäki campus

**Expected result:**
- Classified as `general`
- Live intent detected ("find me") → web search forced
- Returns live listing counts from Vuokraovi for Riihimäki area
- May also include KB reference to HOPS Peltosaari

**Actual result:**
- Classified as `general` ✅
- Live intent triggered web search ✅
- Bot returned live Vuokraovi results: 114 listings at `/vuokra-asunnot/riihimäki`, 115 at `/vuokra-asunnot/riihimäki/keskusta`, plus HOPS Peltosaari mention ✅

**Status: PASS**

---

### TC-08 — General Query: HOPS single-student eligibility

| Field | Detail |
|---|---|
| **Test Case ID** | TC-08 |
| **Category** | General Query |
| **Classification Stage** | Stage 2 (LLM) |
| **Screenshot** | `test_case_05.jpeg` |

**Input message:**
> I am a single student. Can I apply HOPS Riihimäki?

**Expected result:**
- Classified as `general` (student status is not GDPR Art. 9 sensitive data)
- RAG retrieves HOPS application information
- Bot confirms single students can apply and gives next steps

**Actual result:**
- Classified as `general` ✅
- Bot confirmed that yes, single students can apply to HOPS Riihimäki and suggested contacting HOPS directly or visiting their website for availability details ✅

**Status: PASS**

---

### TC-09 — Sensitive Query: Disability (keyword match)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-09 |
| **Category** | Sensitive Query — GDPR Art. 9 Health / Disability Data |
| **Classification Stage** | Stage 1 (Keyword scan) |
| **Triggered keyword** | `disability` |
| **Screenshot** | `test_case_06.jpeg` |

**Input message:**
> Search for accessible apartments for someone with a disability

**Expected result:**
- Stage 1 keyword scan detects `disability` (GDPR Art. 9 — health category)
- Classified as `sensitive` immediately, no LLM processing
- Privacy redirect response shown in amber bubble

**Actual result:**
- Stage 1 keyword scan detected `disability` ✅
- Bot responded with standard privacy redirect to `arrival@hamk.fi` ✅
- Amber highlighted bubble displayed ✅
- No personal health data sent to LLM ✅

**Status: PASS**

---

### TC-10 — Sensitive Query: Pregnancy + housing (keyword match)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-10 |
| **Category** | Sensitive Query — GDPR Art. 9 Family Situation |
| **Classification Stage** | Stage 1 (Keyword scan) |
| **Triggered keyword** | `pregnant` |
| **Screenshot** | `test_case_06.jpeg` |

**Input message:**
> Find me family housing, I am pregnant

**Expected result:**
- Stage 1 keyword scan detects `pregnant`
- Classified as `sensitive` immediately
- Privacy redirect shown, no LLM involvement

**Actual result:**
- Stage 1 keyword scan detected `pregnant` ✅
- Bot responded with standard privacy redirect to `arrival@hamk.fi` ✅
- Amber highlighted bubble displayed ✅

**Status: PASS**

---

### TC-11 — General Query: HOPS application process

| Field | Detail |
|---|---|
| **Test Case ID** | TC-11 |
| **Category** | General Query |
| **Classification Stage** | Stage 2 (LLM) |
| **Screenshot** | `test_case_06.jpeg` |

**Input message:**
> What is the application process for HOPS apartments?

**Expected result:**
- Classified as `general`
- RAG retrieves HOPS application procedure from KB
- Bot explains the application steps, validity period, and deadline rules

**Actual result:**
- Classified as `general` ✅
- Bot responded with correct KB-based information: submit application through HAMK student housing portal, application valid for 3 months, accepted only up to a certain time limit before intended move-in date ✅

**Status: PASS**

---

### TC-12 — Regression: Mustiala sauna (bug fix verification)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-12 |
| **Category** | General Query — Regression Test |
| **Classification Stage** | Stage 2 (LLM) |
| **Bug** | High L2 distance (1.203) was triggering web search; model returned irrelevant apartment listings instead of KB answer |
| **Fix** | Updated system prompt: KB answers take priority — if KB clearly answers the question, answer and STOP without mixing in web results |
| **Screenshot (before fix)** | `test_case_05.jpeg` |
| **Screenshot (after fix)** | `test_case_07_bug_fixed.jpeg` |

**Input message:**
> Does Mustiala have a sauna?

**Expected result (after fix):**
- Classified as `general`
- Model leads with KB answer confirming the lakeside sauna
- No irrelevant apartment listings mixed into the response

**Actual result (before fix):**
- Web search fired (avg L2 distance 1.203 > threshold 0.95) ✅
- Model ignored KB and returned generic apartment listings from Oikotie — incorrect ❌

**Actual result (after fix):**
- Model correctly led with: *"Yes, the Mustiala Campus has a lakeside sauna"* ✅
- Supplementary web results about Mustialan Kievari sauna facilities included ✅
- No irrelevant apartment listings ✅

**Status: PASS (after fix)**

---

### TC-13 — Regression: Bus timetable (bug fix verification)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-13 |
| **Category** | General Query — Regression Test (Non-Housing Web Search) |
| **Classification Stage** | Stage 2 (LLM) |
| **Bug** | `search_finnish_housing()` was called for all queries including non-accommodation ones; returned irrelevant housing results, and model fell back to hallucinated "check the HOPS website" answer |
| **Fix** | Added `_is_housing_query()` routing — non-housing queries skip `search_finnish_housing()` and go directly to `web_search()` |
| **Screenshot (before fix)** | `test_case_05.jpeg` |
| **Screenshot (after fix)** | `test_case_07_bug_fixed.jpeg` |

**Input message:**
> What is the bus timetable from Hämeenlinna to Helsinki?

**Expected result (after fix):**
- Classified as `general`
- `_is_housing_query()` returns False → goes directly to `web_search()`
- Returns real transport results (FlixBus, Matkahuolto, OnniBus) with schedules and URLs

**Actual result (before fix):**
- `search_finnish_housing()` called first, returned housing results unrelated to buses ❌
- Model responded: *"I don't have information on the bus timetable. Check the HOPS website."* — hallucinated and wrong ❌

**Actual result (after fix):**
- `_is_housing_query()` correctly identified this as non-housing ✅
- `web_search()` called directly → returned FlixBus, OnniBus, Matkahuolto results ✅
- Bot recommended checking FlixBus website for latest schedules, with relevant links ✅

**Status: PASS (after fix)**

---

## Test Summary

| TC ID | Input Message | Type | Stage | Web Search | Status |
|---|---|---|---|---|---|
| TC-01 | "Hi, can you help me find a room?" | General | 2 (LLM) | No | PASS |
| TC-02 | "How do I find accommodation in Hämeenlinna?" | General | 2 (LLM) | No | PASS |
| TC-03 | "I have a chronic illness and need a ground floor room." | Sensitive | 1 (Keyword) | No | PASS |
| TC-04 | "I am pregnant, do I qualify for family housing?" | Sensitive | 1 (Keyword) | No | PASS |
| TC-05 | "Is there housing near the Riihimäki campus?" | General | 2 (LLM) | No | PASS |
| TC-06 | "Can you search Hämeenlinna apartments on Vuokraovi for me?" | General | 2 (LLM) | Yes (live intent) | PASS |
| TC-07 | "Find me a room near Riihimäki campus" | General | 2 (LLM) | Yes (live intent) | PASS |
| TC-08 | "I am a single student. Can I apply HOPS Riihimäki?" | General | 2 (LLM) | No | PASS |
| TC-09 | "Search for accessible apartments for someone with a disability" | Sensitive | 1 (Keyword) | No | PASS |
| TC-10 | "Find me family housing, I am pregnant" | Sensitive | 1 (Keyword) | No | PASS |
| TC-11 | "What is the application process for HOPS apartments?" | General | 2 (LLM) | No | PASS |
| TC-12 | "Does Mustiala have a sauna?" *(regression)* | General | 2 (LLM) | Yes | PASS (after fix) |
| TC-13 | "What is the bus timetable from Hämeenlinna to Helsinki?" *(regression)* | General | 2 (LLM) | Yes | PASS (after fix) |

**Total: 13 / 13 PASS**

---

## Notes

- **TC-01 / TC-02 regression:** An earlier version incorrectly classified general queries as sensitive due to: (1) wrong Ollama model name (`llama3` vs `llama3.2`), (2) substring keyword matching (`"ill"` firing inside `"still"`), and (3) an overly vague LLM classification prompt. All three were fixed before these test cases were recorded.
- **TC-06 / TC-07 — Live intent:** The `_has_live_intent()` function detects phrases like "can you search", "find me", "show me" and forces web search regardless of RAG distance. This handles cases where the KB mentions a platform (e.g. Vuokraovi) but the user clearly wants live results.
- **TC-09 / TC-10 — Sensitive UI:** Amber-highlighted bubble with left border is shown for all sensitive responses to make the privacy redirect visually distinct from normal answers.
- **TC-12 regression root cause:** Mustiala sauna query scores avg L2 distance 1.203 (above 0.95 threshold) because the KB text about the sauna uses different vocabulary than the query. Web search fires correctly, but the model was ignoring the KB. Fixed by prioritising KB answers in the system prompt.
- **TC-13 regression root cause:** `search_finnish_housing()` uses `site:vuokraovi.com OR site:oikotie.fi OR site:hops.fi` — these sites have no bus timetable data. Returning empty/irrelevant results caused the model to hallucinate a HOPS reference. Fixed by routing non-housing queries directly to `web_search()`.
- **Privacy guarantee:** In TC-03, TC-04, TC-09, TC-10, the user's health and family situation data never reaches the Ollama LLM — the keyword scan fires in Stage 1 before any LLM call is made.
