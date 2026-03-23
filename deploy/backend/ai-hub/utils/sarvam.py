"""
Sarvam AI utils for deploy/backend/ai-hub
- Saarika v2: Speech-to-Text (22 Indian languages, auto-detect)
- Bulbul v3:  Text-to-Speech (11 Indian languages, natural voices)
- state → language mapping for regional voice selection
"""
import os, io, base64, logging, re
import requests
from typing import Optional

logger = logging.getLogger(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE    = "https://api.sarvam.ai"

# State → language code (22 Indian languages)
STATE_TO_LANG = {
    "Uttar Pradesh":"hi","Bihar":"hi","Madhya Pradesh":"hi","Rajasthan":"hi",
    "Uttarakhand":"hi","Haryana":"hi","Himachal Pradesh":"hi","Jharkhand":"hi",
    "Chhattisgarh":"hi","Delhi":"hi","Maharashtra":"mr","West Bengal":"bn",
    "Tamil Nadu":"ta","Andhra Pradesh":"te","Telangana":"te","Karnataka":"kn",
    "Kerala":"ml","Gujarat":"gu","Punjab":"pa","Odisha":"or","Goa":"en",
    # Northeast defaults to Hindi
    "Assam":"hi","Tripura":"hi","Meghalaya":"hi","Manipur":"hi",
    "Nagaland":"hi","Mizoram":"hi","Arunachal Pradesh":"hi","Sikkim":"hi",
    "J&K":"hi","Ladakh":"hi",
}

SARVAM_LANG_CODES = {
    "hi":"hi-IN","bn":"bn-IN","ta":"ta-IN","te":"te-IN","kn":"kn-IN",
    "ml":"ml-IN","mr":"mr-IN","gu":"gu-IN","pa":"pa-IN","or":"or-IN","en":"en-IN",
}

# Bulbul v3 speaker voices per language
VOICES = {
    "hi-IN":"ritu","bn-IN":"roopa","ta-IN":"shruti","te-IN":"kavitha",
    "kn-IN":"aditya","ml-IN":"priya","mr-IN":"neha","gu-IN":"ishita",
    "pa-IN":"rohan","or-IN":"ritu","en-IN":"amelia",
}

AUDIO_MIME = {
    "wav":"audio/wav","mp3":"audio/mpeg","m4a":"audio/x-m4a",
    "ogg":"audio/ogg","webm":"audio/webm","flac":"audio/flac","aac":"audio/aac",
}


def lang_for_state(state: Optional[str]) -> str:
    return STATE_TO_LANG.get(state or "", "hi")


def sarvam_lang_code(lang: str) -> str:
    return SARVAM_LANG_CODES.get(lang, "hi-IN")


# ── STT ───────────────────────────────────────────────────────────────────────
def transcribe(audio_bytes: bytes, fmt: str = "wav", lang_hint: str = None) -> tuple[str, str]:
    """
    Sarvam Saarika v2.5 STT. Returns (transcript, detected_language_code).
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY not set")

    fmt_clean = fmt.lstrip(".").lower()
    mime = AUDIO_MIME.get(fmt_clean, "audio/wav")

    data = {"model": "saarika:v2.5"}
    if lang_hint and lang_hint != "unknown":
        data["language_code"] = lang_hint
    # Note: with_timestamps removed — not supported in all versions

    files = {"file": (f"audio.{fmt_clean}", io.BytesIO(audio_bytes), mime)}
    resp = requests.post(
        f"{SARVAM_BASE}/speech-to-text",
        headers={"api-subscription-key": SARVAM_API_KEY},
        files=files, data=data, timeout=30
    )
    if not resp.ok:
        logger.error(f"Sarvam STT error {resp.status_code}: {resp.text[:500]}")
    resp.raise_for_status()
    result = resp.json()
    transcript    = result.get("transcript", "").strip()
    detected_lang = result.get("language_code", lang_hint or "hi-IN")  # e.g. "hi-IN"
    return transcript, detected_lang


# ── TTS ───────────────────────────────────────────────────────────────────────
def speak(text: str, state: Optional[str] = None) -> bytes:
    """
    Speak text in the appropriate Indian language for the user's state.
    Uses Sarvam Bulbul v3. Falls back to gTTS if key not set.
    """
    lang      = lang_for_state(state)
    lang_code = sarvam_lang_code(lang)

    if SARVAM_API_KEY:
        try:
            return _bulbul(text, lang_code)
        except Exception as e:
            logger.warning(f"Sarvam TTS failed: {e} — falling back to gTTS")

    return _gtts_fallback(text, lang)


def _bulbul(text: str, lang_code: str) -> bytes:
    # Clean text for TTS
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = re.sub(r'₹', 'rupay ', text)
    text = re.sub(r'%', ' pratishat ', text)
    text = text.strip()

    speaker = VOICES.get(lang_code, "ritu")
    payload = {
        "inputs": [text],
        "target_language_code": lang_code,
        "speaker": speaker,
        "pace": 0.95,
        "enable_preprocessing": True,
        "model": "bulbul:v3",
    }
    resp = requests.post(
        f"{SARVAM_BASE}/text-to-speech",
        headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
        json=payload, timeout=30
    )
    resp.raise_for_status()
    audios = resp.json().get("audios", [])
    if not audios:
        raise ValueError("No audio from Sarvam")
    return base64.b64decode(audios[0])


def _gtts_fallback(text: str, lang: str = "hi") -> bytes:
    try:
        from gtts import gTTS
        import io as _io
        buf = _io.BytesIO()
        gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"gTTS fallback also failed: {e}")
        raise RuntimeError("TTS unavailable: both Sarvam and gTTS failed") from e
