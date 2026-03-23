"""
Agent Router — Yojna Setu AI Hub (Deploy)
Groq-powered one-question-at-a-time eligibility interview.
"""
import os
import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent Interview"])

# ── Language configs ──────────────────────────────────────────────────────────
# Maps our internal language key → (Sarvam lang code, native name, instructions)
LANG_CONFIGS = {
    "hi":  {"code": "hi-IN", "name": "Hindi",   "instructions": "Conduct the ENTIRE interview in simple, friendly Hindi (Devanagari script). Use clear Hindi sentences."},
    "en":  {"code": "en-IN", "name": "English",  "instructions": "Conduct the ENTIRE interview in simple Indian English. Be warm and friendly."},
    "bn":  {"code": "bn-IN", "name": "Bengali",  "instructions": "Conduct the ENTIRE interview in Bengali (বাংলা). Use simple, conversational Bengali."},
    "ta":  {"code": "ta-IN", "name": "Tamil",    "instructions": "Conduct the ENTIRE interview in Tamil (தமிழ்). Use simple, conversational Tamil."},
    "te":  {"code": "te-IN", "name": "Telugu",   "instructions": "Conduct the ENTIRE interview in Telugu (తెలుగు). Use simple, conversational Telugu."},
    "kn":  {"code": "kn-IN", "name": "Kannada",  "instructions": "Conduct the ENTIRE interview in Kannada (ಕನ್ನಡ). Use simple, conversational Kannada."},
    "mr":  {"code": "mr-IN", "name": "Marathi",  "instructions": "Conduct the ENTIRE interview in Marathi (मराठी). Use simple, conversational Marathi."},
    "gu":  {"code": "gu-IN", "name": "Gujarati", "instructions": "Conduct the ENTIRE interview in Gujarati (ગુજરાતી). Use simple, conversational Gujarati."},
    "pa":  {"code": "pa-IN", "name": "Punjabi",  "instructions": "Conduct the ENTIRE interview in Punjabi (ਪੰਜਾਬੀ). Use simple, conversational Punjabi."},
}
DEFAULT_LANG = "hi"


def _build_system(lang: str = "hi") -> str:
    """Build language-aware system prompt."""
    cfg = LANG_CONFIGS.get(lang, LANG_CONFIGS[DEFAULT_LANG])
    return f"""You are Yojna Sathi, a warm and helpful government scheme eligibility advisor for Indian citizens.

LANGUAGE RULE: {cfg['instructions']}
Do NOT switch to any other language. ALL responses must be in {cfg['name']} only.

Conduct a one-question-at-a-time eligibility interview. Build this profile step by step:
state → age → gender → occupation → monthly_income → bpl_card → land_owned (if farmer) → disability

After 7 questions OR enough info, give final scheme recommendations with:
- Scheme name + benefit amount
- Top 3 documents to carry to CSC
- Helpline number
- End with the local-language equivalent of: "Please visit your nearest CSC centre with these documents!"

Rules:
- ONE question per response — never two questions at once
- Warm, simple, encouraging tone
- If user seems confused, rephrase more simply
"""

_sessions: dict[str, list] = {}


class StartRequest(BaseModel):
    session_id: Optional[str] = None
    language:   Optional[str] = "hi"  # ISO-639-1 code: hi, en, ta, bn, te, kn, mr, gu, pa


class AnswerRequest(BaseModel):
    session_id: str
    answer:     str


class AgentResponse(BaseModel):
    session_id: str
    message:    str
    is_complete: bool
    turn:       int
    language:   str = "hi"   # so frontend knows which language to TTS in


def _client() -> Groq:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not configured")
    return Groq(api_key=key)


def _session(sid: str) -> dict:
    if sid not in _sessions:
        _sessions[sid] = {"history": [], "turn": 0, "language": DEFAULT_LANG}
    return _sessions[sid]


def _ask_groq(system: str, history: list, user_prompt: str = None) -> str:
    messages = [{"role": "system", "content": system}] + history[-14:]
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})
    c = _client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )
    return c.choices[0].message.content


@router.post("/start", response_model=AgentResponse)
async def start(req: StartRequest):
    sid  = req.session_id or str(uuid.uuid4())
    lang = req.language if req.language in LANG_CONFIGS else DEFAULT_LANG
    state = _session(sid)
    state["history"]  = []
    state["turn"]     = 1
    state["language"] = lang

    system = _build_system(lang)
    try:
        reply = _ask_groq(
            system, [],
            "Start the interview! Greet the user warmly and ask the FIRST question only (which state are you from?). Respond ONLY in the chosen language."
        )
        state["history"].append({"role": "assistant", "content": reply})
        return AgentResponse(session_id=sid, message=reply, is_complete=False, turn=1, language=lang)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AgentResponse)
async def answer(req: AnswerRequest):
    state = _sessions.get(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found. Call /agent/start first.")

    lang   = state.get("language", DEFAULT_LANG)
    system = _build_system(lang)

    state["history"].append({"role": "user", "content": req.answer})
    state["turn"] += 1
    turn = state["turn"]

    force_recommend = turn >= 8
    extra = "Now give final scheme recommendations — we have enough information. Respond only in the chosen language." if force_recommend else None

    try:
        reply = _ask_groq(system, state["history"], extra)
        state["history"].append({"role": "assistant", "content": reply})
        return AgentResponse(
            session_id=req.session_id,
            message=reply,
            is_complete=force_recommend,
            turn=turn,
            language=lang,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear(session_id: str):
    _sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}
