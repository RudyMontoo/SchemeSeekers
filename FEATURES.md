# Yojna Setu — Features & Tech Stack (Updated)

> Version 2.0 | Updated: Feb 2026 | Team: 4 members

---

## 🌟 Features

### 1. Multilingual "Apanapan" Onboarding
- **Vernacular Greeting Engine** — detects user location/profile and greets in local language (Namaste, Vanakkam, Khamma Gani)
- **No-Type NLP Search** — users type problems, not scheme names (*"Ghar banane ke liye paisa"* instead of *"PMAY-G"*)
- **Dialect-Aware Voice Toggle** — persistent microphone using ASR, understands Hinglish + regional accents

### 2. "Yojna Sathi" (Interactive AI Agent)
- **Conversational Agent** — friendly 2D avatar using TTS in a human-like voice
- **Step-by-Step Eligibility Interview** — asks one adaptive question at a time based on previous answers
- **Interruption Handling** — re-explains using simpler metaphors if the user is confused

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

### 5. "Sahayak" Connectivity (Physical Help)
- **GPS-Based CSC Discovery** — nearest Common Service Centre on integrated map with contact details
- **Priority Ranking** — schemes sorted by ease of application + urgency of need

### 6. Zero-Retention Security (Privacy-First)
- **Volatile RAM Processing** — document images never written to disk
- **Automatic PII Masking** — OpenCV + regex detects and blurs Aadhaar/PAN before AI sees the data

---

## 🛠️ Tech Stack

### Architecture: Microservices (Java–Python Tango)

```
React.js Website (Frontend)
        │
        ▼
Spring Boot API Gateway (Java 17)
        │
        ├──► FastAPI AI Hub (Python)    ← LangChain + ChromaDB + Whisper + Gemini
        │         └──► Status Tracker  ← BeautifulSoup scrapers for 6 government portals
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
| LLM | Google Gemini / GPT-4o |
| Voice | OpenAI Whisper (Hinglish STT) |
| **Status Tracker** | **BeautifulSoup4 + Requests (live portal scraping)** |

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
