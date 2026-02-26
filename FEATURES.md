# Yojna Setu — Features & Tech Stack (Updated)

> Version 2.0 | Updated: Feb 2026 | Team: 4 members

---

## 🌟 Features

### 1. Multilingual "Apanapan" Onboarding
- **Vernacular Greeting Engine** — detects user location/profile and greets in local language (Namaste, Vanakkam, Khamma Gani)
- **No-Type NLP Search** — users type problems, not scheme names (*"Ghar banane ke liye paisa"* instead of *"PMAY-G"*)
- **Dialect-Aware Voice Toggle** — persistent microphone using ASR, understands Hinglish + regional accents
- **Session Memory** — chatbot remembers full conversation context across messages (`/chat` + `/chat/stream`)
- **Hallucination Guard** — if no scheme matches, honestly redirects to myscheme.gov.in instead of hallucinating

### 2. "Yojna Sathi" (Interactive AI Agent)
- **Conversational Agent** — friendly 2D avatar using TTS in a human-like voice
- **Step-by-Step Eligibility Interview** — asks one adaptive question at a time based on previous answers
- **Interruption Handling** — re-explains using simpler metaphors if the user is confused
- **Expanded Hinglish Understanding** — recognizes *"mere paas nahi hai"*, *"bilkul"*, *"vidyarthi"*, *"kisan"*, *"berozgar"* and more
- **Eligibility Re-Ranking** — retrieves 3× more candidates, scores 0–1000 by profile match, returns top-5
- **Document Checklist API** — `GET /agent/checklist` returns required documents per scheme for CSC visits

### 3. Jan-Sahayak Document Lens
- **Legality & Validity Scan** — OCR extracts expiry dates, detects official seals/stamps
- **Document-to-Action Bridge** — if a document is missing, provides:
  - 60-second YouTube tutorials on how to get it
  - One-tap links to the official government portal

### 4. 🆕 Live Scheme Application Status Tracker
- **Real-time Status Scraper** — fetches live application status directly from government portals using Aadhaar / Application ID / Registration Number
- **Visual Progress Pipeline** — shows a step-by-step completion bar (e.g., Foundation → Lintel → Roof → Completed for PMAY-G)
- **Supported Schemes (Phase 1):**

  | Scheme | Portal Scraped | Input Needed |
  |--------|---------------|-------------|
  | PM Kisan Samman Nidhi | pmkisan.gov.in | Aadhaar |
  | PM Awas Yojana - Gramin | pmayg.nic.in | Registration No. |
  | MGNREGS (MNREGA) | nrega.nic.in | Job Card No. |
  | National Scholarship Portal | scholarships.gov.in | Application ID |
  | Ayushman Bharat PM-JAY | beneficiary.nha.gov.in | Aadhaar |
  | PM Ujjwala Yojana | mylpg.in | Application ID |

- **Hinglish Status Messages** — status shown in simple Hinglish (*"Aapka ghar ka 2nd installment aa gaya — lintel level complete!"*)
- **Retry Logic** — 3 automatic retries with exponential backoff on slow/failing government portals


### 5. "Sahayak" Connectivity (Physical Help)
- **GPS-Based CSC Discovery** — nearest Common Service Centre on integrated map with contact details
- **Priority Ranking** — schemes sorted by ease of application + urgency of need

### 6. Zero-Retention Security (Privacy-First)
- **Volatile RAM Processing** — document images never written to disk
- **Automatic PII Masking** — OpenCV + regex detects and blurs Aadhaar/PAN before AI sees the data

### 7. 🆕 Guided Application Wizard (Multilingual)
- **Zero-Complexity Apply Flow** — step-by-step instructions in the user's **own language**, not a complex govt URL
- **Auto Language Detection** — `?state=Tamil Nadu` → Tamil, `?state=West Bengal` → Bengali, `?language=mr-IN` → Marathi
- **Powered by Sarvam Mayura** — translates every step, document name, hint, and note into the user's regional script
- **Offline CSC Mode** — *"Go to CSC with these 4 documents"* + exact helpline + hours
- **Tracking ID Guide** — tells what ID the CSC gives (Aadhaar / Registration No. / Job Card) for use in Status Tracker
- **In-Memory Cache** — same scheme+language never translated twice
- **10 Schemes** — PM Kisan, PMAY-G, MGNREGA, Ayushman, NSP, Ujjwala, Jan Dhan, PMMVY, Mudra, Fasal Bima

---

## 🛠️ Tech Stack

### Architecture: Microservices (Java–Python Tango)

```
React.js Website (Frontend)
        │
        ▼
Spring Boot API Gateway (Java 17)
        │
        ├──► FastAPI AI Hub (Python)    ← Groq Llama 3.3 70B + ChromaDB + Sarvam AI
        │         ├──► Status Tracker  ← BeautifulSoup scrapers for 6 government portals
        │         ├──► Apply Wizard    ← Sarvam Mayura multilingual guides
        │         └──► Help & Discover ← OpenStreetMap + YouTube Data API v3
        │
        └──► Flask OCR Worker (Python)  ← PaddleOCR + OpenCV
```

### 1. Core Backend (Brain & Security)
| Component | Technology |
|-----------|-----------|
| Framework | Spring Boot (Java 17/21) |
| Database | PostgreSQL |
| Security | JWT + Spring Security |
| Role | API Gateway, user profiles, scheme history, CSC locations |

### 2. AI & Intelligence Hub
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (Python) |
| Agent | LangChain ConversationChain |
| Vector DB | ChromaDB |
| LLM | **Groq (Llama 3.3 70B)** — free, fast |
| Voice STT | **Sarvam Saarika v2** (22 Indian languages) + Whisper fallback |
| Voice TTS | **Sarvam Bulbul v3** (11 Indian languages, 30+ voices) |
| Translation | **Sarvam Mayura** — Hinglish → Tamil/Bengali/Marathi etc. |
| **Status Tracker** | **BeautifulSoup4 + Requests (live portal scraping)** |
| **Apply Wizard** | **Sarvam Mayura multilingual step-by-step guides** |
| **Help & Discovery** | **OpenStreetMap Overpass API + YouTube Data API v3** |

### 3. OCR & Image Worker
| Component | Technology |
|-----------|-----------|
| Framework | Flask (Python) |
| OCR Engine | PaddleOCR / Tesseract |
| Image Processing | OpenCV |

### 4. Frontend
| Component | Technology |
|-----------|-----------|
| Framework | **React.js** (Web App) |
| Styling | Tailwind CSS |
| Voice/Camera | Browser Web APIs (MediaDevices) |
| UI Focus | Mobile-first responsive (Android browser users) |

---

## 👥 Team Roles

| Member | Role | Key Tasks |
|--------|------|-----------|
| **Member 1 (You)** | AI/ML Lead | FastAPI, LangChain RAG, Yojna Sathi agent, Whisper STT, PII masking, **Status Tracker scrapers** |
| Member 2 | Backend Specialist | Spring Boot API, JWT auth, PostgreSQL schema |
| Member 3 | Generalist/Integration | Flask OCR, PaddleOCR, scheme PDF scraping, Maps/YouTube APIs |
| Member 4 | Frontend/UI UX | React.js screens, camera/mic hooks, multilingual UI |

---

## 📦 Your Deliverables (Member 1)

1. `ai_service/` — FastAPI server
2. `ai_service/routers/chat.py` — Yojna Sathi agent endpoint
3. `ai_service/routers/voice.py` — Whisper transcription endpoint
4. `ai_service/routers/status_tracker.py` — Live scheme status scraper *(NEW)*
5. `ai_service/rag/` — ChromaDB ingestion + retrieval
6. `ai_service/utils/pii_masker.py` — Aadhaar/PAN redaction
7. `ai_service/data/schemes/` — 150 schemes across 10 sectors (JSON)
