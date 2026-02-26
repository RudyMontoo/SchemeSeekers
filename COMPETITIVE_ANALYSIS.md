# 🏆 Yojna Setu — Competitive Analysis

> **"myScheme tells you what schemes exist. Yojna Setu tells you which ones YOU qualify for — in your language, by voice, without needing internet literacy."**

---

## 🇮🇳 Existing Players in India

### 1. myScheme.gov.in (Government of India)
- **What it does:** Official central portal to browse and filter 500+ government schemes by category, age, income, gender etc.
- **Strengths:** Authoritative, comprehensive scheme database, regularly updated
- **Gaps:**
  - English/Hindi text UI only — no voice
  - No AI matching — user must know what to look for
  - No document scanner, no CSC locator, no status tracker
  - Not accessible to low-literacy rural users

### 2. UMANG App (Unified Mobile Application for New-age Governance)
- **What it does:** Single app aggregating 2,000+ government services (EPFO, PMKVY, IT filing, etc.)
- **Strengths:** Very wide service coverage, single login, biometric support
- **Gaps:**
  - Portal aggregator — not an AI assistant
  - No eligibility interview or personalized matching
  - No voice agent or Hinglish understanding
  - Requires reasonable smartphone/digital literacy

### 3. Jan Samarth Portal (jansamarth.in)
- **What it does:** Credit-linked government schemes (PM Mudra, PM SVANidhi, PMEGP, education loans)
- **Strengths:** Direct bank integration, end-to-end loan application
- **Gaps:**
  - Finance/credit schemes only
  - No voice, no OCR, no multilingual support
  - Cannot help with non-credit schemes (housing, health, agriculture, etc.)

### 4. DigiLocker
- **What it does:** Secure digital wallet for storing government documents (Aadhaar, PAN, marksheets, RC, DL)
- **Strengths:** 200M+ users, legally valid documents, widely integrated
- **Gaps:**
  - Not a scheme discovery or eligibility tool
  - Complementary to Yojna Setu (we can link to DigiLocker for document retrieval)

### 5. State-Specific Portals (Aaple Sarkar, Seva Sindhu, eSampark etc.)
- **What they do:** State government services — income/caste certificates, ration cards, subsidies
- **Strengths:** Authoritative for state services, direct application
- **Gaps:**
  - Single-state only — no cross-scheme discovery
  - No AI, no voice, no OCR
  - Each state has different UX — no unified interface

---

## ⚡ Feature-by-Feature Comparison

| Feature | myScheme | UMANG | Jan Samarth | Yojna Setu |
|---|:---:|:---:|:---:|:---:|
| AI eligibility matching | ❌ | ❌ | ❌ | ✅ |
| Voice-first (Hinglish + dialects) | ❌ | ❌ | ❌ | ✅ |
| Conversational interview agent | ❌ | ❌ | ❌ | ✅ |
| OCR document scanner | ❌ | ❌ | ❌ | ✅ |
| Live scheme status tracker | ❌ | Partial | ❌ | ✅ |
| CSC centre locator (GPS) | ❌ | ❌ | ❌ | ✅ |
| Guided Apply Wizard (Offline CSC steps) | ❌ | ❌ | ❌ | ✅ |
| Multilingual wizard (Tamil/Bengali/Marathi…) | ❌ | ❌ | ❌ | ✅ (Sarvam Mayura) |
| Multilingual voice (12+ Indian languages) | ❌ | Partial | ❌ | ✅ (Sarvam AI) |
| PII masking / privacy-first | ❌ | ❌ | ❌ | ✅ |
| Document help guide + YouTube tutorials | ❌ | ❌ | ❌ | ✅ |
| Works for low-literacy users | ❌ | ❌ | ❌ | ✅ |
| Central + State schemes | ✅ | Partial | ❌ | ✅ |
| Free to use | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Yojna Setu's Unique Value Proposition

### Who is our target user?
A rural Indian citizen who:
- Speaks Hindi, Bhojpuri, Marathi, or Tamil — **not English**
- Has a basic Android smartphone but **limited digital literacy**
- Lives **30–60 km from the nearest CSC centre**
- Has **never successfully applied** for a government scheme despite being eligible
- May be eligible for 5–10 schemes but **doesn't know which ones or how to apply**

### Why existing apps fail this user
| Problem | myScheme response | Yojna Setu response |
|---|---|---|
| "I don't know scheme names" | Must browse categories manually | Ask "Ghar chahiye?" → AI finds PMAY, IAY, PMGSY |
| "I can't type Hindi" | No voice input | Full voice conversation in Hinglish |
| "My document is missing" | No guidance | OCR scans, detects missing docs, YouTube tutorial + portal link |
| "Did my application go through?" | No status | Live scraping of 6 govt portals |
| "Where do I go for help?" | No CSC finder | GPS-based CSC locator |

---

## 📊 Market Opportunity

- **~500 million** Indians are eligible for at least one government scheme
- **~300 million** have never successfully applied (digital divide)
- Government schemes worth **₹15+ lakh crore** disbursed annually — significant under-utilisation
- **myScheme.gov.in** sees ~10M visits/month but low application conversion

---

## 🔮 Roadmap Differentiators (Future)

| Feature | Status |
|---|---|
| Sarvam AI TTS in 12 Indian languages | ✅ Integrated |
| WhatsApp bot integration | Planned |
| Offline mode (PWA) for low-connectivity areas | Planned |
| Direct online application via Spring Boot gateway | Planned |
| Family profile — apply for multiple members | Planned |

---

> **In summary:** No existing Indian app combines AI-powered eligibility matching + voice-first interaction + OCR + multilingual support + CSC locator + guided offline apply wizard in a single product aimed at rural, low-literacy users. **Yojna Setu is the first.**

---

## 🤖 AI/Language Stack

| Layer | Technology | Languages Supported |
|---|---|---|
| LLM (RAG Chat) | Groq Llama 3.3 70B | Hinglish |
| STT (Voice input) | Sarvam Saarika v2 | 22 Indian languages |
| TTS (Voice output) | Sarvam Bulbul v3 | 11 Indian languages, 30+ voices |
| Translation | Sarvam Mayura | hi↔ta, hi↔bn, hi↔mr, hi↔te, hi↔kn, hi↔ml, hi↔gu, hi↔pa, hi↔or |
| Apply Guide | Sarvam Mayura | Guides delivered in user's script (Tamil, Bengali, Marathi…) |
