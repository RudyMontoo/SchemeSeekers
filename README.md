<div align="center">
  <h1>🏛️ Yojna Setu</h1>
  <h3>AI-Powered Government Scheme Assistant</h3>
  <p><b>"Connecting Citizens to their Rights — Jan Jan ko Yojana se Jodo 🇮🇳"</b></p>
  
  <p>
    <a href="https://github.com/RudyMontoo/Yojna_Setu/issues">
      <img src="https://img.shields.io/badge/version-2.0-blue?style=for-the-badge" alt="Version 2.0" />
    </a>
    <a href="https://python.org">
      <img src="https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10" />
    </a>
    <a href="https://fastapi.tiangolo.com/">
      <img src="https://img.shields.io/badge/FastAPI-0.110-teal?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    </a>
    <a href="https://react.dev">
      <img src="https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
    </a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Schemes_Indexed-419-orange?style=flat-square" alt="419 Schemes" />
    <img src="https://img.shields.io/badge/Languages_Supported-22_Indian-purple?style=flat-square" alt="22 Languages" />
  </p>
</div>

---

## 📖 Table of Contents
1. [What is Yojna Setu?](#-what-is-yojna-setu)
2. [System Architecture](#-system-architecture)
3. [Key Features](#-key-features)
4. [Tech Stack](#-tech-stack)
5. [Getting Started](#-getting-started)
6. [API Endpoints](#-api-endpoints)
7. [Team](#-team)

---

## 🌟 What is Yojna Setu?

Thousands of government schemes exist, but most citizens never access them due to **complex portals**, **language barriers**, and **lack of awareness**. 

**Yojna Setu bridges that gap** by providing an highly-accessible, conversational AI interface. Whether the user speaks Hindi, Bengali, or Marathi, our AI assistant evaluates their profile, recommends the exact schemes they are eligible for, and checks their live application status.

- 🗣️ **Voice-first interaction** — *No typing needed.*
- 🌐 **Nationwide Coverage** — *Supports 22 Indian languages.*
- 🤖 **Adaptive AI Interview** — *Step-by-step dynamic eligibility matching.*
- 🔒 **Privacy-first Platform** — *Zero PII retention.*

---

## 🏗️ System Architecture

```mermaid
graph TD;
    %% Styling
    classDef frontend fill:#61DAFB,stroke:#333,stroke-width:2px,color:#000;
    classDef gateway fill:#6DB33F,stroke:#333,stroke-width:2px,color:#fff;
    classDef backend fill:#009688,stroke:#333,stroke-width:2px,color:#fff;
    classDef ai fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff;
    classDef db fill:#3F51B5,stroke:#333,stroke-width:2px,color:#fff;

    User((User)) -->|Voice / Text / Scan| UI[React.js Frontend<br/>Mobile-First UI]:::frontend
    UI -->|HTTPS| API[Spring Boot API Gateway<br/>Auth & Routing]:::gateway
    
    API -->|RAG / Intents| AIHub[FastAPI AI Hub<br/>Python 3.10]:::backend
    API -->|Base64 Image| OCRWorker[Flask OCR Worker<br/>PaddleOCR + OpenCV]:::backend
    
    AIHub -->|Vector Queries| ChromaDB[(ChromaDB<br/>419 Schemes)]:::db
    AIHub -->|Generative Prompts| Gemini[Google Gemini 2.0 Flash<br/>LLM]:::ai
    AIHub -->|STT / TTS| Sarvam[Sarvam AI API<br/>22 Languages]:::ai
    AIHub -->|Offline Fallback STT| Whisper[OpenAI Whisper<br/>Local inference]:::ai
    AIHub -->|Web Scraping| GovtPortals[[6 Government Portals<br/>Live Status Retrieval]]:::db
```

---

## ✨ Key Features

### 1. 🤖 Yojna Sathi — Conversational Eligibility Agent
An adaptive, multi-turn interview that builds a dynamic profile to recommend the best schemes.
- Understands natural Hinglish (e.g., *"mere paas nahi hai"* → mapped to boolean logic).
- Re-ranks schemes 3× by dynamic eligibility score (0–100).
- Auto-generates document checklists for Common Service Center (CSC) visits.

### 2. 🎙️ Bidirectional Voice Pipeline
Total hands-free experience tailored for Indian dialects.
- **Auto-State Detection:** Detects user's state to pick the correct regional language & voice actor.
- **Primary STT/TTS:** Sarvam Saarika v2 & Bulbul v3 APIs.
- **Fail-safe Mode:** Automatically switches to locally hosted OpenAI Whisper models if APIs go down.

### 3. 💬 Low-Latency RAG Chatbot
Type or speak any problem in plain language.
- Powered by **Google Gemini 2.0 Flash** + **ChromaDB** with `all-MiniLM-L6-v2` embeddings.
- Maintains strict conversational session memory via `langchain_core`.
- Streaming endpoints allow tokens to stream natively to the frontend.

### 4. 🛰️ Live Status Tracker
Real-time application status dynamically scraped from active portals rather than caching stale data.
- Built-in 3x retry mechanism with **exponential backoff**.
- Supports 6 major portals including PM Kisan, MGNREGS, and Ayushman Bharat.

### 5. 🛡️ PII Masker (Privacy Guard)
Automatically intercepts Prompts before reaching the LLM and masks sensitive entities utilizing fast Regex sanitization (`Aadhaar`, `PAN`, `Phone Numbers`).

### 6. 📷 Jan-Sahayak Lens (OCR)
Zero-retention, memory-only document scanner utilizing **PaddleOCR CNN pipelines** and **OpenCV** (Auto-deskew, warping, adaptive thresholding) to pull document constraints.

---

## 🛠️ Tech Stack

<details open>
<summary><b>Click to expand</b></summary>

| Category | Technology |
|----------|-----------|
| **Frontend UI** | React 18, Vite, Vanilla CSS (Glassmorphism design) |
| **Backend Core** | FastAPI (Python 3.10+), Spring Boot (Java 17) |
| **LLM Engine** | Google Gemini 2.0 Flash, LangChain |
| **Vector Database**| ChromaDB, `all-MiniLM-L6-v2` embedding logic |
| **Vision/OCR** | OpenCV, PaddleOCR, Flask Worker |
| **Audio/Voice** | Sarvam AI (Saarika, Bulbul), OpenAI Whisper, gTTS |
| **Web Scraping** | BeautifulSoup4 (BS4), Python Requests |

</details>

---

## 🚀 Getting Started

### Prerequisites
- Node.js v18+ (For Frontend)
- Python 3.10+ (For AI Service)
- NVIDIA GPU recommended for local Whisper fallback

### 1. Configure the AI Engine (Backend)

```bash
# Clone the repository
git clone https://github.com/RudyMontoo/SchemeSeekers.git
cd SchemeSeekers

# Navigate to the AI Service and install Python dependencies
cd ai_service
pip install -r requirements.txt

# Setup Environment Keys
cp .env.example .env
```

Ensure your `.env` contains:
```env
GEMINI_API_KEY=your_gemini_api_key
SARVAM_API_KEY=your_sarvam_api_key   # Optional but heavily recommended
WHISPER_MODEL=base
```

**Run the Backend:**
```bash
# Embed 419 schemes into local ChromaDB
python ingest.py

# Start the uvicorn server
uvicorn main:app --reload --port 8000
```
> API Docs available at `http://localhost:8000/docs`

### 2. Configure the UI (Frontend)

```bash
# Open a new terminal from the project root
cd frontend

# Install Node dependencies
npm install

# Start the Vite Development Server
npm run dev
```
> Frontend available at `http://localhost:5173`

---

## 📡 API Endpoints 

<details>
<summary><b>View Complete API Reference</b></summary>

| HTTP Method | API Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Diagnostic status (ChromaDB count, DB state, LLM validation) |
| `POST` | `/chat/` | RAG Chatbot with conversation memory |
| `POST` | `/chat/stream` | Stream generated tokens directly |
| `POST` | `/agent/start` | Start eligibility interview |
| `POST` | `/agent/answer` | Provide interview answers to AI Agent |
| `GET` | `/agent/checklist` | Request physical document list |
| `POST` | `/voice/query` | Translate Voice mp3 -> Text -> RAG Query -> Voice MP3 |
| `POST` | `/status/check` | Fetch Live Scraped Status from portals |
| `POST` | `/ocr/scan` | Zero-retention document processing |

</details>

---

## 👥 Team & Architecture Roles

| Member | Focus / Role |
|--------|------|
| **Rudra (AI/ML Lead)** | FastAPI, LangChain RAG & Memory, Agent Pipeline, STT/TTS Fallbacks, PII Masker, Web Scraping |
| **Member 2** | Spring Boot API Gateway, Security Auth, Route Mapping |
| **Member 3** | Flask OCR, PaddleOCR Integration, External Maps Integration |
| **Member 4** | React Frontend, Responsive Design System, Hardware APIs (Camera/Mic) |

---

<div align="center">
  <p><i>This project is built for social good. All data is sourced directly from verifiable Indian government public portals.</i></p>
  <p><b>MSE-2 Evaluated Project</b></p>
</div>
