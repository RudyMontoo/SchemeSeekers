"""
Voice Conversation Router — Full Audio Agent
Adds bidirectional voice to the Yojna Sathi agent:

  User speaks → Whisper STT → Agent → gTTS → Audio response

Endpoints:
  POST /voice/conversation/start    → Returns audio: "Namaskar! State batao?"
  POST /voice/conversation/answer   → Accepts audio, returns audio response
  POST /voice/conversation/chat     → One-shot voice chat (no session)
"""
import os
import uuid
import tempfile
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice/conversation", tags=["voice_agent"])

SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}
MAX_FILE_MB = 25

# ── Welcome message variants ──────────────────────────────────────────────────
WELCOME_TEXT_HI = (
    "Namaskar! Main Yojna Sathi hun. "
    "Main aapko sarkari yojanaon ki jaankari dunga. "
    "Pehle mujhe batayein aap kaun se state se hain?"
)

SCHEME_INTRO_HI = "Bahut achha! Aapke liye yeh sarkari yojanaen hain: "


# ── Helpers ───────────────────────────────────────────────────────────────────
def _speak(text: str, state: str = None) -> bytes:
    """
    Convert text to audio. Uses Sarvam Bulbul v3 if API key is set,
    else falls back to gTTS. Auto-selects language based on user's state.
    """
    from ai_service.utils.sarvam import speak_for_state, SARVAM_API_KEY
    if SARVAM_API_KEY:
        logger.info(f"TTS via Sarvam Bulbul v3 (state={state})")
        return speak_for_state(text, state)
    # Fallback
    from ai_service.utils.tts import text_to_speech
    return text_to_speech(text, lang='hi')


async def _transcribe_upload(file: UploadFile, state: str = None) -> str:
    """
    Transcribe audio. Uses Sarvam Saarika v2 if API key set, else Whisper.
    Sarvam auto-detects Indian language — no need to specify.
    """
    import os as _os
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise HTTPException(400, f"Unsupported audio format: {suffix}")
    content = await file.read()
    if len(content) / (1024 * 1024) > MAX_FILE_MB:
        raise HTTPException(400, "Audio too large (max 25MB)")

    from ai_service.utils.sarvam import SARVAM_API_KEY, sarvam_transcribe
    if SARVAM_API_KEY:
        logger.info("STT via Sarvam Saarika v2")
        result = sarvam_transcribe(content, audio_format=suffix.lstrip("."))
        return result["transcript"]

    # Fallback: Whisper
    import tempfile, whisper
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        model_size = _os.getenv("WHISPER_MODEL", "base")
        model = whisper.load_model(model_size)
        result = model.transcribe(
            tmp_path,
            initial_prompt="Hindi-English Hinglish sarkari yojana conversation.",
            fp16=False
        )
        return result["text"].strip()
    finally:
        _os.unlink(tmp_path)


def _build_scheme_audio(schemes: list, message: str, state: str = None) -> bytes:
    """Convert scheme list to spoken audio in user's language."""
    parts = [message or SCHEME_INTRO_HI]
    for i, s in enumerate(schemes[:3], 1):  # speak top 3 only
        name = s.get("name", "")
        benefit = s.get("benefit", "")
        score = s.get("eligibility_score", 0)
        parts.append(
            f"Number {i}: {name}. "
            f"Yogyata score {score} pratishat. "
            f"{benefit[:100] if benefit else ''}"
        )
    parts.append(
        "Adhik jaankari ke liye apne CSC kendra ya myscheme.gov.in par jayein. "
        "Dhanyavaad!"
    )
    full_text = " ... ".join(parts)
    return _speak(full_text, state=state)


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/start")
async def voice_start_session():
    """
    Start a new voice agent session.
    Returns MP3 audio of the welcome + first question.
    Also returns the session_id as a response header.
    """
    from ai_service.routers.agent_router import _sessions
    from ai_service.agent.yojna_sathi import UserProfile, get_next_question

    session_id = str(uuid.uuid4())
    profile = UserProfile()
    _sessions[session_id] = {"profile": profile, "question_idx": 0}

    first_q = get_next_question(profile)
    # Speak welcome + first question in Hindi (state not yet known)
    full_text = WELCOME_TEXT_HI + " " + (first_q["question_hi"] or first_q["question_en"])
    audio_bytes = _speak(full_text, state=None)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "X-Session-Id": session_id,
            "X-Question-En": first_q["question_en"],
            "X-Progress": "0",
            "Content-Disposition": "inline; filename=question.mp3",
        }
    )


@router.post("/answer")
async def voice_answer(
    audio: UploadFile = File(..., description="User's spoken answer (WAV/MP3/M4A)"),
    session_id: str = Form(..., description="Session ID from /start"),
):
    """
    Submit voice answer → get voice response (next question or final schemes).

    Flow:
      1. Whisper transcribes user's audio
      2. Answer is parsed into UserProfile
      3. Agent generates next question OR final scheme list
      4. gTTS converts response to audio
      5. Returns MP3 audio + metadata headers
    """
    from ai_service.routers.agent_router import _sessions, _retrieve_schemes
    from ai_service.agent.yojna_sathi import get_next_question, parse_answer

    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found. Call /voice/conversation/start first.")

    # Step 1: Transcribe
    transcript = await _transcribe_upload(audio)
    logger.info(f"Transcribed: '{transcript}'")

    if not transcript or len(transcript.strip()) < 2:
        repeat_text = "Maafi kijiye, clearly nahi suna. Kripya dobara bolein."
        audio_bytes = _speak(repeat_text, state=profile.state)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "X-Session-Id": session_id,
                "X-Transcript": "(unclear)",
                "X-Done": "false",
                "X-Progress": "0",
            }
        )

    profile = session["profile"]

    # Step 2: Parse answer
    current_q = get_next_question(profile)
    if current_q:
        parse_answer(current_q, transcript, profile)

    # Step 3: Get next question
    next_q = get_next_question(profile)
    progress = profile.completion_pct()

    # Step 4a: If done → retrieve schemes and speak results
    if next_q is None or progress >= 100:
        del _sessions[session_id]
        schemes = await _retrieve_schemes(profile)

        message = (
            f"Bahut achha! Aapke profile ke hisaab se "
            f"{len(schemes)} sarkari yojanaen mili hain — "
        )
        audio_bytes = _build_scheme_audio(
            [{"name": s.name, "benefit": s.benefit, "eligibility_score": s.eligibility_score}
             for s in schemes],
            message,
            state=profile.state,
        )

        scheme_names = " | ".join(s.name for s in schemes[:3])
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "X-Session-Id": session_id,
                "X-Transcript": transcript[:200],
                "X-Done": "true",
                "X-Progress": "100",
                "X-Schemes": scheme_names[:500],
                "Content-Disposition": "inline; filename=schemes.mp3",
            }
        )

    # Step 4b: Speak next question in user's language
    next_text = next_q.get("question_hi") or next_q["question_en"]
    next_audio = _speak(next_text, state=profile.state)

    return Response(
        content=next_audio,
        media_type="audio/mpeg",
        headers={
            "X-Session-Id": session_id,
            "X-Transcript": transcript[:200],
            "X-Done": "false",
            "X-Progress": str(progress),
            "X-Question-En": next_q["question_en"],
            "Content-Disposition": "inline; filename=question.mp3",
        }
    )


@router.post("/chat")
async def voice_chat_oneshot(
    audio: UploadFile = File(..., description="User's spoken question (any topic)"),
    state: Optional[str] = Form(default=None),
):
    """
    One-shot voice query (no session needed):
    User asks any question by voice → get spoken scheme recommendations.

    Example: User says "Kya koi housing scheme hai?" → Agent speaks back matching schemes.
    """
    from ai_service.utils.tts import text_to_speech

    # Step 1: Transcribe (Sarvam Saarika or Whisper)
    transcript = await _transcribe_upload(audio, state=state)

    if not transcript.strip():
        audio_bytes = _speak(
            "Maafi kijiye, aapki awaz clearly nahi aayi. Phir se try karein.",
            state=state
        )
        return Response(content=audio_bytes, media_type="audio/mpeg",
                        headers={"X-Transcript": "(unclear)"})

    # Step 2: RAG retrieval
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        chroma_dir = Path(__file__).parent.parent / "chroma_db"
        client = chromadb.PersistentClient(path=str(chroma_dir))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        col = client.get_collection("yojna_setu_schemes", embedding_function=ef)

        where = {"state": {"$in": [state, "Central"]}} if state else None
        results = col.query(query_texts=[transcript], n_results=3, where=where)

        docs = results["documents"][0]
        metas = results["metadatas"][0]

        # Build spoken response
        spoken_parts = [f"Aapne pucha: {transcript[:80]}. Yeh yojanaen relevant hain:"]
        for i, (doc, meta) in enumerate(zip(docs, metas), 1):
            name = meta.get("name", "")
            benefit_line = next(
                (l.replace("Benefit:", "").strip() for l in doc.split("\n") if l.startswith("Benefit:")),
                ""
            )
            spoken_parts.append(
                f"Number {i}: {name}. {benefit_line[:100] if benefit_line else ''}"
            )
        spoken_parts.append(
            "Aur jaankari ke liye apne nazdiki CSC centre jayein ya "
            "my scheme dot gov dot in visit karein."
        )

        spoken_text = " ... ".join(spoken_parts)

    except Exception as e:
        logger.error(f"RAG error in voice chat: {e}")
        spoken_text = (
            "Maafi kijiye, abhi scheme database se connect nahi ho pa raha. "
            "Kripya myscheme.gov.in par jaayein."
        )

    # Step 3: TTS via Sarvam Bulbul (or gTTS fallback) in user's language
    audio_bytes = _speak(spoken_text, state=state)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "X-Transcript": transcript[:200],
            "Content-Disposition": "inline; filename=reply.mp3",
        }
    )


@router.get("/test-tts")
async def test_tts(
    text: str = "Namaskar! Main Yojna Sathi hun.",
    state: Optional[str] = None,
):
    """Test TTS in user's state language (Sarvam Bulbul v3 or gTTS fallback)."""
    audio_bytes = _speak(text, state=state)
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=test.mp3"}
    )
