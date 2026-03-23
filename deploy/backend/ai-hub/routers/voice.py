"""
Voice Agent Router — deploy/backend/ai-hub
==========================================
Adds audio I/O to the Yojna Sathi interview:

  Browser mic → WebM/audio → Sarvam Saarika v2 STT → Groq LLM → Sarvam Bulbul v3 TTS → MP3

Endpoints:
  POST /voice/start    → Returns MP3 of first question ("Aap kaun se state se hain?")
  POST /voice/answer   → Accepts audio file → returns MP3 of next question / final schemes
  GET  /voice/test-tts → Quick TTS test
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from utils.sarvam import speak, transcribe, SARVAM_API_KEY, SARVAM_LANG_CODES
# Reuse the same session store and Groq helper from agent.py
from routers.agent import _sessions, _ask_groq, _build_system, LANG_CONFIGS, DEFAULT_LANG

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice Agent"])

SUPPORTED_FMTS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".aac"}
MAX_MB = 25

WELCOME_HI = (
    "Namaskar! Main Yojna Sathi hun. "
    "Main aapki government scheme dhundne mein madad karunga. "
    "Sabse pehle mujhe batayein — aap kaun se state se hain?"
)


# ── Helpers ───────────────────────────────────────────────────────────────────
async def _read_audio(file: UploadFile, max_mb: int = MAX_MB) -> tuple[bytes, str]:
    """Read and validate audio upload. Returns (bytes, extension)."""
    ext = Path(file.filename or "audio.wav").suffix.lower()
    if ext not in SUPPORTED_FMTS:
        raise HTTPException(400, f"Unsupported format '{ext}'. Use: {', '.join(SUPPORTED_FMTS)}")
    content = await file.read()
    if len(content) > max_mb * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {max_mb}MB)")
    return content, ext.lstrip(".")


def _state_from_session(sid: str) -> Optional[str]:
    """Try to extract the user's state from conversation history."""
    history = _sessions.get(sid, {}).get("history", [])
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"].lower()
            from utils.sarvam import STATE_TO_LANG
            for state in STATE_TO_LANG:
                if state.lower() in content:
                    return state
    return None


def _speak_in_lang(text: str, lang_code: str) -> bytes:
    """
    TTS using explicit Sarvam lang_code (e.g. 'hi-IN').
    Does NOT depend on state — uses the user's chosen language directly.
    Falls back to gTTS on failure.
    """
    from utils.sarvam import _bulbul, _gtts_fallback, SARVAM_LANG_CODES
    short_lang = next((k for k, v in SARVAM_LANG_CODES.items() if v == lang_code), "hi")
    try:
        return _bulbul(text, lang_code)
    except Exception as e:
        logger.warning(f"Bulbul TTS failed ({e}), gTTS fallback lang={short_lang}")
        return _gtts_fallback(text, short_lang)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/start")
async def voice_start(
    language: str = Form(default=DEFAULT_LANG, description="ISO-639-1 language code: hi, en, ta, bn, te, kn, mr, gu, pa"),
):
    """
    Start a new voice agent session in the chosen language.
    Returns: MP3 audio of the welcome greeting + first question.
    """
    if not SARVAM_API_KEY:
        raise HTTPException(503, "SARVAM_API_KEY not configured — voice unavailable")

    lang = language if language in LANG_CONFIGS else DEFAULT_LANG
    lang_code = SARVAM_LANG_CODES.get(lang, "hi-IN")

    sid = str(uuid.uuid4())
    _sessions[sid] = {"history": [], "turn": 1, "language": lang}

    # Build language-aware system prompt
    system = _build_system(lang)

    try:
        first_q_text = _ask_groq(
            system, [],
            "Start! Greet the user warmly and ask the FIRST question only (which state are you from?). Respond only in the chosen language."
        )
    except Exception as e:
        raise HTTPException(503, f"Groq unavailable: {e}")

    _sessions[sid]["history"].append({"role": "assistant", "content": first_q_text})

    # Convert to audio in the chosen language
    try:
        audio = _speak_in_lang(first_q_text, lang_code)
    except Exception as e:
        raise HTTPException(503, f"TTS failed: {e}")

    logger.info(f"Voice session started: {sid} | lang={lang} | q: {first_q_text[:50]}...")
    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={
            "X-Session-Id": sid,
            "X-Question":   quote(first_q_text[:300]),
            "X-Language":   lang,
            "X-Turn":       "1",
            "X-Done":       "false",
            "Content-Disposition": "inline; filename=question.mp3",
        },
    )


@router.post("/answer")
async def voice_answer(
    audio: UploadFile = File(..., description="User's spoken answer (WAV/MP3/WebM/OGG)"),
    session_id: str   = Form(..., description="Session ID from POST /voice/start"),
):
    """
    Submit a voice answer → receive a voice response (next question or final schemes).

    Flow:
      1. Sarvam Saarika v2 transcribes user audio
      2. Transcription sent to Groq as user message
      3. Groq produces next question or final recommendations
      4. Sarvam Bulbul v3 speaks the response in the user's state language
      5. Returns MP3 + metadata headers
    """
    if not SARVAM_API_KEY:
        raise HTTPException(503, "SARVAM_API_KEY not configured — voice unavailable")

    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found — call POST /voice/start first")

    # 1. Read & transcribe audio (auto-detects language)
    content, fmt = await _read_audio(audio)
    try:
        transcript, detected_lang_code = transcribe(content, fmt=fmt)  # e.g. "hi-IN"
        logger.info(f"[{session_id}] Transcript: '{transcript}' | Detected lang: {detected_lang_code}")
    except Exception as e:
        logger.error(f"STT error: {e}")
        retry_text = "Maafi kijiye, aapki awaz clearly nahi aayi. Ek baar aur bolein please."
        return Response(
            content=speak(retry_text, state=None),
            media_type="audio/mpeg",
            headers={"X-Session-Id": session_id, "X-Transcript": "(STT error)", "X-Done": "false"},
        )

    # AUTO-LANGUAGE: update session language from detected speech
    # Reverse map "hi-IN" -> "hi"
    detected_short = next(
        (k for k, v in SARVAM_LANG_CODES.items() if v == detected_lang_code),
        session.get("language", DEFAULT_LANG)
    )
    if detected_short in LANG_CONFIGS and detected_short != session.get("language"):
        logger.info(f"[{session_id}] Auto-switching language: {session['language']} → {detected_short}")
        session["language"] = detected_short

    if not transcript.strip():
        lang = session.get("language", DEFAULT_LANG)
        lang_code = SARVAM_LANG_CODES.get(lang, "hi-IN")
        retry_msgs = {
            "hi": "Kuch suna nahi. Thoda zyada paas aake bolein?",
            "en": "Sorry, I couldn't hear you. Please speak a bit louder.",
            "ta": "Kேட்கவில்லை. கொஞ்சம் தெளிவாக பேசுங்கள்.",
            "bn": "শুনতে পাইনি। একটু জোরে বলুন।",
            "te": "వినబడలేదు. కొంచెం స్పష్టంగా మాట్లాడండి.",
        }
        retry_text = retry_msgs.get(lang, retry_msgs["hi"])
        return Response(
            content=_speak_in_lang(retry_text, lang_code),
            media_type="audio/mpeg",
            headers={"X-Session-Id": session_id, "X-Transcript": "(empty)", "X-Done": "false"},
        )

    # 2. Add to history & call Groq with language-aware prompt
    lang      = session.get("language", DEFAULT_LANG)
    lang_code = SARVAM_LANG_CODES.get(lang, "hi-IN")
    system    = _build_system(lang)

    session["history"].append({"role": "user", "content": transcript})
    session["turn"] += 1
    turn = session["turn"]

    force_done  = turn >= 8
    extra_prompt = f"Now give final scheme recommendations. Respond only in {LANG_CONFIGS[lang]['name']}." if force_done else None

    try:
        reply = _ask_groq(system, session["history"], extra_prompt)
    except Exception as e:
        raise HTTPException(503, f"Groq unavailable: {e}")

    session["history"].append({"role": "assistant", "content": reply})

    # 4. TTS in user's chosen language (not state-guessed)
    try:
        audio_bytes = _speak_in_lang(reply, lang_code)
    except Exception as e:
        raise HTTPException(503, f"TTS failed: {e}")

    logger.info(f"[{session_id}] Turn {turn} | lang={lang} | reply: {reply[:50]}...")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "X-Session-Id":        session_id,
            "X-Transcript":        quote(transcript[:300]),
            "X-Reply":             quote(reply[:300]),
            "X-Turn":              str(turn),
            "X-Done":              "true" if force_done else "false",
            "X-Detected-Language": lang,   # so frontend can show which lang was detected
            "Content-Disposition": "inline; filename=reply.mp3",
        },
    )


@router.get("/test-tts")
async def test_tts(
    text:  str = "Namaskar! Main Yojna Sathi hun. Aap kaun se state se hain?",
    state: Optional[str] = None,
):
    """Quick TTS test — GET /voice/test-tts?text=Hello&state=Tamil+Nadu"""
    if not SARVAM_API_KEY:
        raise HTTPException(503, "SARVAM_API_KEY not configured")
    try:
        audio = speak(text, state=state)
        return Response(content=audio, media_type="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=test.mp3"})
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/status")
async def voice_status():
    return {
        "voice_available":   bool(SARVAM_API_KEY),
        "stt_model":         "sarvam-saarika:v2",
        "tts_model":         "sarvam-bulbul:v3",
        "supported_formats": list(SUPPORTED_FMTS),
        "languages":         ["hi","bn","ta","te","kn","ml","mr","gu","pa","or","en"],
    }
