# 👥 Yojna Setu — Team Member Docs

> This document outlines the responsibilities, deliverables, and integration points for each team member.
> **Member 1 (AI/ML — Rudra)** has already completed the FastAPI AI Hub. This doc covers the remaining three members.

---

## 🔗 How All Parts Connect

```
[Member 4 — React Frontend]
        │
        │  REST API calls (JSON + audio)
        ▼
[Member 2 — Spring Boot API Gateway]
        │
        ├──► [Member 1 — FastAPI AI Hub] ← DONE ✅
        │         (port 8000)
        │
        └──► [Member 3 — Flask OCR Worker]
                  (port 5000)
```

---

---

# 👤 Member 2 — Backend Specialist (Spring Boot)

## Role
Java API Gateway — the central hub that the frontend talks to. Routes requests to the AI service and OCR worker, handles user accounts, and stores historical data.

## Tech Stack
- **Java 17+**, Spring Boot 3.x
- **PostgreSQL** — main database
- **JWT + Spring Security** — authentication
- **RestTemplate / WebClient** — to call Member 1's FastAPI (port 8000)

---

## 📋 Deliverables

### 1. User Authentication
- `POST /api/auth/register` — create account (name, phone, state, language preference)
- `POST /api/auth/login` → returns JWT token
- `GET /api/auth/profile` — get user profile

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  phone VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(100),
  state VARCHAR(50),
  preferred_language VARCHAR(10) DEFAULT 'hi',
  caste_category VARCHAR(10),
  created_at TIMESTAMP
);
```

---

### 2. Proxy Routes to AI Service (Member 1)
Spring Boot acts as a gateway — it forwards these to FastAPI on `localhost:8000`:

| Spring Boot Route | Forwards To (FastAPI) | Description |
|---|---|---|
| `POST /api/chat` | `POST /chat/` | Hinglish chatbot |
| `POST /api/agent/start` | `POST /agent/start` | Start interview |
| `POST /api/agent/answer` | `POST /agent/answer` | Submit answer |
| `POST /api/voice/transcribe` | `POST /voice/transcribe` | Whisper STT |
| `POST /api/voice/conversation/start` | `POST /voice/conversation/start` | Voice agent |
| `POST /api/voice/conversation/answer` | `POST /voice/conversation/answer` | Voice agent answer |
| `POST /api/status/check` | `POST /status/check` | Live status tracker |

> **Why proxy through Spring Boot?**
> So the frontend only needs one base URL. Spring Boot adds JWT auth checks before forwarding.

---

### 3. Scheme History
Save every scheme the user was recommended — so they can revisit later.

```sql
CREATE TABLE scheme_history (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  scheme_name VARCHAR(200),
  sector VARCHAR(50),
  state VARCHAR(50),
  apply_url TEXT,
  eligibility_score INT,
  viewed_at TIMESTAMP DEFAULT NOW()
);
```

- `GET /api/history` — get user's past scheme recommendations
- `POST /api/history` — save a scheme (called after agent completes)

---

### 4. CSC (Common Service Centre) Locator
Store CSC centre data and serve nearest ones by GPS coordinates.

```sql
CREATE TABLE csc_centres (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200),
  state VARCHAR(50),
  district VARCHAR(100),
  address TEXT,
  phone VARCHAR(15),
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6),
  services TEXT[]  -- ['pmkisan', 'pmay', 'aadhaar']
);
```

- `GET /api/csc/nearby?lat=28.61&lon=77.20&radius=5` → returns nearest CSC centres
- Pre-populate from: [locator.csccloud.in](https://locator.csccloud.in) (public CSV available)

---

### 5. Application Status History
Cache the status tracker results per user.

- `GET /api/status/history` — user's previously checked scheme statuses
- `POST /api/status/save` — save a status check result

---

## ⚡ Integration Points with Other Members

| Connects To | How |
|---|---|
| Member 1 (FastAPI) | HTTP proxy calls to `localhost:8000` |
| Member 3 (Flask OCR) | HTTP proxy calls to `localhost:5000` |
| Member 4 (Frontend) | Exposes REST API on port 8080, CORS enabled for `localhost:3000` |

---

---

# 👤 Member 3 — OCR & Integration Specialist (Flask)

## Role
Document scanner — uses PaddleOCR and OpenCV to extract text from uploaded documents, check validity, and detect missing fields.

## Tech Stack
- **Python**, Flask
- **PaddleOCR** — primary OCR engine (handles Hindi + English)
- **Tesseract** — fallback OCR
- **OpenCV** — image preprocessing + seal/stamp detection
- **PyMuPDF / pdf2image** — PDF to image conversion

---

## 📋 Deliverables

### 1. Document Upload & OCR Endpoint

`POST /ocr/scan` (multipart form — image or PDF)

```json
Response:
{
  "document_type": "aadhaar",
  "extracted_text": "...",
  "fields": {
    "name": "Rajesh Kumar",
    "dob": "15/08/1985",
    "aadhaar_number": "XXXX-XXXX-1234",   ← masked by Member 1's PII masker
    "address": "Village Rampur, UP"
  },
  "validity": {
    "is_valid": true,
    "expiry_date": null,
    "has_official_seal": true
  },
  "missing_fields": []
}
```

---

### 2. Supported Document Types

| Document | Fields to Extract |
|---|---|
| Aadhaar Card | Name, DOB, Address, UID (masked) |
| PAN Card | Name, PAN number (masked), DOB |
| Ration Card | Family members, BPL/APL status |
| Income Certificate | Annual income, issuing authority |
| Caste Certificate | Category (SC/ST/OBC), state |
| Land Record (Khasra) | Survey no., area in acres, owner name |
| Bank Passbook | Account number (masked), bank name, IFSC |
| Disability Certificate | Disability %, type |

---

### 3. Document Validity Scanner

- Detects **expiry dates** — alerts if expired
- Detects **official seals/stamps** using OpenCV contour detection
- Checks for **required fields** — if a field is missing, flags it

---

### 4. Missing Document Bridge

When a document is missing:

`GET /ocr/guide?document=income_certificate&state=UP`

```json
{
  "document": "Income Certificate",
  "how_to_get": "Visit your Tehsil/SDM office with Aadhaar and Ration card",
  "youtube_tutorial": "https://youtube.com/watch?v=...",
  "official_portal": "https://edistrict.up.gov.in",
  "time_to_get": "3-7 working days"
}
```

---

### 5. Privacy — Images Never Stored

```python
# Process in RAM only — never write to disk
@app.route('/ocr/scan', methods=['POST'])
def scan():
    file_bytes = request.files['document'].read()  # RAM only
    image = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
    result = ocr_engine.ocr(image)
    # file_bytes goes out of scope → garbage collected
    return jsonify(extract_fields(result))
```

---

## ⚡ Integration Points

| Connects To | How |
|---|---|
| Member 2 (Spring Boot) | Spring Boot proxies `/api/ocr/*` to Flask on `localhost:5000` |
| Member 1 (FastAPI) | After OCR, extracted profile fields can be sent to `/agent/answer` to auto-fill interview |

---

---

# 👤 Member 4 — Frontend Developer (React.js)

## Role
The user-facing mobile-first web app. Handles voice recording, camera access, map display, and all UI screens.

## Tech Stack
- **React.js** (v18+)
- **Tailwind CSS** — styling
- **Web APIs**: `MediaDevices` (mic + camera), `AudioContext` (visualizer)
- **React Router** — navigation
- **Axios** — API calls to Spring Boot (port 8080)

---

## 📋 Deliverables

### 1. Screens / Pages

| Screen | Description |
|---|---|
| 🏠 Home / Language Select | Greeting in user's language, pick language |
| 🎙️ Voice Agent Screen | Avatar + mic button + audio visualizer |
| 💬 Chat Screen | Text chat with scheme results |
| 📊 Scheme Results | Cards showing matched schemes with apply button |
| 📡 Status Tracker | Input Aadhaar/App ID → show progress pipeline |
| 📷 Document Scanner | Camera upload → show extracted fields + validity |
| 🗺️ CSC Locator Map | Nearest CSC centres on map with call/directions |
| 📁 My History | Past scheme searches and status checks |

---

### 2. Voice Agent UI (Most Important Screen)

```
┌─────────────────────────────┐
│   [2D Avatar — animated]    │
│   Mouth moves while speaking│
│                             │
│  "Aap kaun se state se hain?"│
│                             │
│   ████████░░░░  57% done   │
│                             │
│   [🎙️ TAP TO SPEAK]        │
│                             │
│   Transcript: "Maharashtra" │
└─────────────────────────────┘
```

**How audio works with Member 1's API:**
```javascript
// 1. Start session
const res = await axios.post('/api/voice/conversation/start');
const sessionId = res.headers['x-session-id'];
const audio = new Audio(URL.createObjectURL(new Blob([res.data])));
audio.play(); // play agent's welcome message

// 2. Record user's voice
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream);
// ... collect chunks ...

// 3. Send to agent
const formData = new FormData();
formData.append('audio', audioBlob, 'answer.webm');
formData.append('session_id', sessionId);
const reply = await axios.post('/api/voice/conversation/answer', formData);

// 4. Play response + check if done
const isDone = reply.headers['x-done'] === 'true';
const progress = reply.headers['x-progress'];
const agentAudio = new Audio(URL.createObjectURL(new Blob([reply.data])));
agentAudio.play();
```

---

### 3. Avatar Animation
While the agent's audio is playing → animate the avatar (talking state).
While listening → show listening animation (pulse/ripple effect).

```javascript
agentAudio.onplay  = () => setAvatarState('talking');
agentAudio.onended = () => setAvatarState('listening');
```

Options (pick one):
- **Lottie JSON animation** — easiest, 2D character
- **CSS keyframe animation** — mouth open/close SVG
- **Simple waveform visualizer** — if avatar design isn't ready

---

### 4. Status Tracker UI — Visual Progress Pipeline

```
PM Kisan — Rajesh Kumar
─────────────────────────────────────
✅ Registered
✅ Aadhaar Verified
✅ Land Verified
✅ Bank Verified
✅ 1st Installment (₹2000)
✅ 2nd Installment (₹2000)
⬜ 3rd Installment (₹2000)  ← current
⬜ Active
```

Data comes from `POST /api/status/check` → `stages[]` array from Member 1.

---

### 5. Document Scanner UI

- Use `<input type="file" accept="image/*" capture="environment">` for mobile camera
- Show extracted fields in a card
- Highlight missing/expired fields in red
- Show "Get this document" button if missing

---

### 6. CSC Map

- Use **Leaflet.js** (free, no API key) or Google Maps Embed
- Pins from `GET /api/csc/nearby?lat=X&lon=Y`
- Each pin shows: name, phone, distance, "Call" + "Directions" buttons

---

## ⚡ Integration Points

| Connects To | How |
|---|---|
| Member 2 (Spring Boot) | All API calls go to `http://localhost:8080/api/...` |
| Member 1 (FastAPI) | Indirectly — via Spring Boot proxy |

---

---

## 📅 Suggested Integration Order

```
Week 1: Member 2 sets up Spring Boot + DB + proxy routes
        Member 3 builds OCR scan endpoint  
        Member 4 builds Home + Chat screens

Week 2: Member 4 builds Voice Agent screen + avatar
        Member 2 adds CSC locator + scheme history
        Member 3 adds validity scanner + missing doc guide

Week 3: Full integration testing
        Member 4 polishes UI + makes mobile-responsive
        Member 2 adds JWT auth
        All: Demo preparation
```

---

> **Questions?** Contact Rudra (AI Lead) for API contracts, request/response formats, and integration help.
