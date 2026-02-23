# 🏛️ Yojna Setu — AI-Powered Government Scheme Assistant

> **"Connecting Citizens to their Rights"**
> A multilingual, voice-first AI platform that helps every Indian citizen discover, check eligibility, and apply for government schemes — in their own language.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![Schemes](https://img.shields.io/badge/schemes-419-orange)
![Languages](https://img.shields.io/badge/languages-22%20Indian-purple)

---

## 🌟 What is Yojna Setu?

Thousands of government schemes exist — but most citizens never access them due to complex portals, language barriers, and lack of awareness. **Yojna Setu bridges that gap** using:

- 🗣️ **Voice-first interaction** — no typing needed
- 🌐 **22 Indian languages** — Hindi, Tamil, Bengali, Telugu, and more
- 🤖 **AI-powered eligibility matching** — finds the right schemes for YOUR profile
- 📡 **Live status tracking** — real-time status from government portals
- 🔒 **Privacy-first** — Aadhaar/PAN never stored or sent to AI raw

---

## 🏗️ System Architecture

```
React.js Frontend (Mobile-first)
        │
        ▼
Spring Boot API Gateway (Java 17)
        │
        ├──► FastAPI AI Hub (Python)     ← This repository
        │         ├── LangChain RAG + ChromaDB
        │         ├── Google Gemini 2.0 Flash
        │         ├── Sarvam AI (STT/TTS — 22 languages)
        │         ├── OpenAI Whisper (local, offline fallback)
        │         └── BeautifulSoup scrapers (6 govt portals)
        │
        └──► Flask OCR Worker (Python)   ← Teammate
                  └── PaddleOCR + OpenCV
```

---

## ✨ Key Features

### 1. 🤖 Yojna Sathi — Conversational AI Agent
An adaptive eligibility interview that builds your profile step-by-step and recommends the most relevant schemes.

- Asks one question at a time in **Hinglish** + regional languages
- Understands natural Hinglish answers: *"mahila"* → female, *"mere paas nahi hai"* → No, *"bilkul"* → Yes
- **Re-ranks schemes 3× by eligibility score** (0–100) before returning top results
- Handles 13+ profile fields: state, age, gender, caste, income, BPL, occupation, disability, etc.
- **New: `/agent/checklist`** — returns document requirements per scheme for CSC visits

### 2. 🎙️ Voice Pipeline — Bidirectional Audio Interview
Full voice-to-voice conversation with the agent.

- **Speech-to-Text**: Sarvam Saarika v2 (primary) → OpenAI Whisper (offline fallback)
- **Text-to-Speech**: Sarvam Bulbul v3 with 30+ natural Indian voices
- **Auto language selection**: detects user's state → picks correct regional language & voice
- Streams MP3 audio directly back — no frontend processing needed

### 3. 💬 RAG Chatbot — Hinglish Scheme Search with Memory
Type any problem in plain language and get scheme recommendations.

- **Per-session conversation memory** — remembers full context across messages in a session
- **No-match hallucination guard** — if no scheme found, redirects to myscheme.gov.in honestly
- **Streaming endpoint** (`/chat/stream`) — tokens stream as Gemini generates for faster UX
- Filters by state + sector for hyper-relevant results
- Powered by **Google Gemini 2.0 Flash** + **ChromaDB** + `langchain_core` memory

### 4. 📡 Live Status Tracker
Real-time application status scraped from official government portals.
- **Auto-retry**: 3 retries with exponential backoff on slow/failing govt portals

| Scheme | Portal | Input |
|--------|--------|-------|
| PM Kisan Samman Nidhi | pmkisan.gov.in | Aadhaar |
| PM Awas Yojana - Gramin | pmayg.nic.in | Registration No. |
| MGNREGS (MNREGA) | nrega.nic.in | Job Card No. |
| National Scholarship Portal | scholarships.gov.in | Application ID |
| Ayushman Bharat PM-JAY | beneficiary.nha.gov.in | Aadhaar |
| PM Ujjwala Yojana | mylpg.in | Application ID |

### 5. 🔒 PII Masker — Privacy First
Automatically detects and redacts sensitive data before it touches any AI model.
- Aadhaar: `9876 5432 1234` → `XXXX-XXXX-XXXX`
- PAN: `ABCDE1234F` → `XXXXXXXXXX`
- Phone: `9876543210` → `XXXXXXXXXX`

### 6. 📚 419 Government Schemes Dataset
Hand-curated and verified across 19 sectors and 36 states/UTs.

| Type | Count |
|------|-------|
| Central Government Schemes | 276 |
| State-Specific Schemes | 143 |
| **Total** | **419** |

Sectors: Agriculture, Health, Education, Housing, Women & Child, SC/ST Welfare, Defence, Employment, Energy, Environment, Digital India, Sports, Fisheries, Tribal, Minority, Senior Citizens, Social Security, Rural Development, Financial Inclusion

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI (Python 3.10+) |
| LLM | Google Gemini 2.0 Flash |
| RAG / Agent | LangChain |
| Conversation Memory | `langchain_core` `InMemoryChatMessageHistory` (per session) |
| Vector Database | ChromaDB |
| Embeddings | `all-MiniLM-L6-v2` (local, free) |
| Primary STT | Sarvam Saarika v2 (22 Indian languages) |
| Fallback STT | OpenAI Whisper (local, offline) |
| Primary TTS | Sarvam Bulbul v3 (natural Indian voices) |
| Fallback TTS | gTTS (Hindi) |
| Translation | Sarvam Mayura v1 |
| Web Scraping | BeautifulSoup4 + Requests (3× retry backoff) |
| PII Detection | Regex (Python `re`) |

---

## 📁 Project Structure

```
ai_service/
├── main.py                         # FastAPI entrypoint
├── rag_chain.py                    # LangChain RAG pipeline
├── ingest.py                       # Scheme JSON → ChromaDB ingestion
├── requirements.txt
│
├── agent/
│   └── yojna_sathi.py              # Interview engine + eligibility scorer
│
├── routers/
│   ├── chat.py                     # POST /chat, /chat/stream, DELETE /chat/session/{id}
│   ├── agent_router.py             # POST /agent/start, /agent/answer, GET /agent/checklist
│   ├── voice.py                    # POST /voice/transcribe, /voice/query
│   ├── voice_conversation.py       # POST /voice/conversation/* (audio ↔ audio)
│   └── status_tracker.py           # POST /status/check — live portal scraping (with retry)
│
├── utils/
│   ├── sarvam.py                   # Sarvam AI STT / TTS / Translation
│   ├── tts.py                      # gTTS fallback
│   └── pii_masker.py               # Aadhaar / PAN / Phone redaction
│
└── data/
    └── schemes/
        ├── *.json                  # Central sector schemes (19 sectors)
        └── states/
            └── *.json              # State schemes (36 states/UTs)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- NVIDIA GPU recommended (for Whisper local inference)

### 1. Clone & Install

```bash
git clone https://github.com/RudyMontoo/Yojna_Setu.git
cd Yojna_Setu/ai_service
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

```env
GEMINI_API_KEY=your_gemini_api_key
SARVAM_API_KEY=your_sarvam_api_key   # optional but recommended
WHISPER_MODEL=base                    # tiny / base / small / medium
```

> **Get free API keys:**
> - Gemini: [aistudio.google.com](https://aistudio.google.com)
> - Sarvam: [dashboard.sarvam.ai](https://dashboard.sarvam.ai)

### 3. Build the Vector Database

```bash
cd ai_service
python ingest.py
# Embeds all 419 schemes into ChromaDB (~2 minutes first time)
```

### 4. Run the Server

```bash
uvicorn ai_service.main:app --reload --port 8000
```

API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/` | Text chatbot — Hinglish scheme search (with session memory) |
| `POST` | `/chat/stream` | **NEW** — Streaming chatbot (tokens stream as generated) |
| `DELETE` | `/chat/session/{id}` | **NEW** — Clear conversation memory for a session |
| `POST` | `/agent/start` | Start eligibility interview |
| `POST` | `/agent/answer` | Submit interview answer |
| `GET` | `/agent/checklist` | **NEW** — Document requirements per scheme (`?query=pm+kisan&state=UP`) |
| `POST` | `/voice/transcribe` | Audio file → text |
| `POST` | `/voice/query` | Audio → schemes (end-to-end) |
| `POST` | `/voice/conversation/start` | Start voice interview (returns MP3) |
| `POST` | `/voice/conversation/answer` | Voice answer → voice response |
| `POST` | `/voice/conversation/chat` | One-shot voice query |
| `POST` | `/status/check` | Live scheme application status |
| `GET` | `/status/schemes` | List trackable schemes |
| `GET` | `/health` | **Updated** — Rich diagnostic (ChromaDB count, API keys, sessions) |
| `GET` | `/docs` | Swagger UI |

---

## 👥 Team

| Member | Role |
|--------|------|
| **Rudra (AI/ML Lead)** | FastAPI, LangChain RAG+Memory, Yojna Sathi agent, Whisper/Sarvam voice pipeline, PII masking, Status Tracker, Streaming API |
| Member 2 | Spring Boot API Gateway, JWT auth, PostgreSQL |
| Member 3 | Flask OCR Worker, PaddleOCR, Maps/YouTube APIs |
| Member 4 | React.js Frontend, Camera/Mic hooks, Multilingual UI |

---

## 📄 License

This project is built for social good. All government scheme data is sourced from official public portals.

---

> *"Jan Jan ko Yojana se Jodo"* — Connect every citizen to their entitlements 🇮🇳
