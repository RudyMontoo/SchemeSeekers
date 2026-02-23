# 🔄 Yojna Setu — Application Workflow

> This document describes the complete user journey and internal data flow for each mode of the Yojna Setu platform.

---

## 🗺️ Overall Entry Flow

```
User Opens App (React Frontend)
        │
        ▼
  Language Selection (Hindi / Tamil / Bengali / Telugu / etc.)
        │
        ▼
  Choose Mode:
  ┌────────────┬───────────┬───────────────┬─────────────────┐
  │ 🎙️ Voice  │ 💬 Chat  │ 📷 Scan Docs │ 📡 Check Status │
  └────────────┴───────────┴───────────────┴─────────────────┘
```

---

## 🎙️ Mode 1 — Voice Interview (Primary Flow)

```
1. User taps "Start"
        │
        ▼
2. POST /voice/conversation/start  →  Spring Boot  →  FastAPI
        │
        ← Returns: MP3 audio ("Namaste! Aap kahan se hain?")
        │
        ▼
3. Frontend plays audio  →  Avatar animates (mouth moves while speaking)
        │
        ▼
4. User speaks answer into mic  (e.g., "Maharashtra")
        │
        ▼
5. POST /voice/conversation/answer  (audio blob + session_id)
        │
        FastAPI internally:
        ├── Sarvam Saarika v2 → STT → "Maharashtra"     (or Whisper fallback)
        ├── PII Masker        → check for Aadhaar/PAN
        ├── parse_answer()    → profile.state = "Maharashtra"
        ├── get_next_question() → "Aapki umar kya hai?"
        ├── Sarvam Bulbul v3  → TTS → MP3               (or gTTS fallback)
        └── Returns: MP3 audio + response headers
                        X-Progress: 23
                        X-Done: false
                        X-Transcript: "Maharashtra"
        │
        ▼
6. Repeat steps 4–5 for ~10–13 adaptive questions
   (questions skip or change based on previous answers)
        │
        ▼
7. Final answer received  (X-Done: true)
        │
        FastAPI internally:
        ├── ChromaDB query with complete user profile
        ├── Eligibility re-ranking: 3× candidates scored 0–100
        └── Returns: Top-5 scheme cards + audio summary
        │
        ▼
8. Frontend shows scheme result cards + plays audio summary
        │
        ▼
9. User taps a scheme card
        │
        ▼
10. GET /agent/checklist?query=<scheme>&state=<state>
        │
        ← Returns: Document list required for that scheme
        │
        ▼
11. "Document Checklist" shown + "Find Nearest CSC Centre" button
```

---

## 💬 Mode 2 — Text Chat Flow

```
1. User types: "Ghar banane ke liye koi scheme hai?"
        │
        ▼
2. POST /chat/  {message, session_id, state, sector}
        │
        FastAPI internally:
        ├── Load session memory (InMemoryChatMessageHistory)
        ├── ChromaDB semantic search (top-5 by embedding similarity)
        ├── No-match guard → if no results: redirect to myscheme.gov.in
        ├── Gemini 2.0 Flash → generate Hinglish response
        └── Save exchange to session memory
        │
        ← Returns: { reply, matched_schemes[], session_id }
        │
        ▼
3. Frontend shows: reply text + scheme cards (name, benefit, apply link)

4. User follows up: "Mere liye kaunsa best hai?"
        │
        ▼ (memory carries the context from step 1 automatically!)
5. Gemini responds with personalized recommendation using full history

─────────────────────────────────────────────
  OR: Use streaming endpoint for faster UX
─────────────────────────────────────────────
2b. POST /chat/stream  → tokens stream token-by-token
    Frontend shows text appearing word by word (like ChatGPT)
```

---

## 📷 Mode 3 — Document Scan Flow (Flask OCR Worker)

```
1. User taps "Scan Document" → Camera / File picker opens
        │
        ▼
2. Image or PDF uploaded
        │
        ▼
3. POST /api/ocr/scan  →  Spring Boot  →  Flask OCR Worker (port 5000)
        │
        PaddleOCR + OpenCV internally:
        ├── PDF → image conversion (if PDF)
        ├── Image preprocessing (denoise, deskew, contrast)
        ├── OCR text extraction (Hindi + English)
        ├── Field extraction (Name, DOB, Aadhaar, PAN, Income, etc.)
        ├── PII masking (Aadhaar/PAN blurred before returning)
        ├── Seal/stamp detection (official document validation)
        └── Expiry date check
        │
        ← Returns:
          {
            document_type: "aadhaar",
            fields: { name, dob, address },
            validity: { is_valid, has_seal },
            missing_fields: []
          }
        │
        ▼
4. Frontend shows:
        ✅ Valid fields (green)
        ❌ Missing / expired fields (red)
        │
        ▼
5. If field missing → "How to get it?" button
        │
        ▼
6. GET /ocr/guide?document=income_certificate&state=UP
        │
        ← Returns: Tehsil address + YouTube link + official portal + time to get
```

---

## 📡 Mode 4 — Live Status Check Flow

```
1. User selects scheme (e.g., PM Kisan)
   User enters identifier (Aadhaar / Application ID / Job Card No.)
        │
        ▼
2. POST /status/check  { scheme_key: "pmkisan", identifier: "XXXX" }
        │
        FastAPI internally (with 3× retry + backoff):
        ├── Scrape official govt portal (e.g., pmkisan.gov.in)
        ├── Parse HTML response
        └── Structure into stages[]
        │
        ← Returns:
          {
            beneficiary_name: "Rajesh Kumar",
            status: "active",
            stages: [
              { name: "Registered",      completed: true  },
              { name: "Aadhaar Verified", completed: true  },
              { name: "1st Installment", completed: true  },
              { name: "2nd Installment", completed: false }
            ],
            message_hi: "Aapka 2nd installment pending hai"
          }
        │
        ▼
3. Frontend shows visual progress pipeline:
        ✅ Registered
        ✅ Aadhaar Verified
        ✅ 1st Installment (₹2000)
        ⬜ 2nd Installment (₹2000)  ← pending
```

---

## 🔐 Security Layer (Runs on Every Request)

```
Every request:
  1. JWT Token verified by Spring Boot Gateway
         │
  2. Request forwarded to FastAPI / Flask worker
         │
  3. PII Masker intercepts any text with Aadhaar / PAN / Phone
         XXXX XXXX XXXX → XXXX-XXXX-XXXX
         ABCDE1234F     → XXXXXXXXXX
         9876543210     → XXXXXXXXXX
         │
  4. AI model receives clean, masked data only
         │
  5. Images processed in RAM only — NEVER written to disk
         │
  6. Session memory cleared when user ends conversation
```

---

## 🔗 Component Communication Summary

```
React Frontend
    │  REST + FormData + Audio Blob
    ▼
Spring Boot Gateway (port 8080) — Auth + Routing
    │                         │
    ▼                         ▼
FastAPI AI Hub           Flask OCR Worker
(port 8000)              (port 5000)
    │
    ├── ChromaDB (local vector DB)
    ├── Gemini 2.0 Flash (LLM)
    ├── Sarvam AI (STT / TTS / Translation)
    ├── OpenAI Whisper (local STT fallback)
    ├── gTTS (local TTS fallback)
    └── BeautifulSoup (web scraping — 6 govt portals)
```

---

> **In one line:** User speaks their problem → AI interviews → Scores 419 schemes → Recommends top matches → Shows documents needed → Finds nearest help centre. 🇮🇳
