"""
Chat Router — Yojna Setu AI Hub (Deploy)
Uses Groq Llama 3.3 70B with scheme data in system prompt.
Persistence: calls Spring Boot Internal API → Supabase PostgreSQL.
"""
import os
import json
import logging
import httpx
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from groq import Groq

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

SPRING_URL = os.getenv("SPRING_BACKEND_URL", "http://localhost:8080")

# ── Load schemes context ───────────────────────────────────────────────────────
_SCHEMES_CONTEXT = ""
_SCHEMES_DATA = []
try:
    _schemes_path = Path(__file__).parent.parent / "data" / "schemes_lite.json"
    with open(_schemes_path, "r", encoding="utf-8") as f:
        _SCHEMES_DATA = json.load(f)
    lines = []
    for s in _SCHEMES_DATA:
        lines.append(
            f"• {s['name']} ({s['sector']}): {s['description']}"
            f" | Eligibility: {s['eligibility']}"
            f" | Benefit: {s['benefit']}"
            f" | Apply: {s['apply_url']}"
            f" | Helpline: {s.get('helpline','')}"
        )
    _SCHEMES_CONTEXT = "\n".join(lines)
except Exception as e:
    logger.warning(f"Could not load schemes: {e}")
    _SCHEMES_CONTEXT = "Refer user to myscheme.gov.in for scheme discovery."

_SYSTEM_PROMPT = f"""You are Yojna Sathi, a friendly AI assistant helping Indian citizens discover and apply for government welfare schemes.
You speak warm, simple Hinglish (Hindi + English mix). Be patient and helpful — many users have low literacy.

GOVERNMENT SCHEMES YOU KNOW ABOUT:
{_SCHEMES_CONTEXT}

RESPONSE RULES:
1. Always respond in simple Hinglish unless user writes in another language — then match their language
2. When user describes their situation, suggest the most fitting scheme with benefit amount
3. Mention documents needed and helpline number for recommended schemes
4. Keep responses under 150 words — short, clear, actionable
5. If user mentions state, tailor advice accordingly (some schemes have state variants)
6. Honest: if no matching scheme, redirect to myscheme.gov.in or call 14555
7. Never fabricate scheme details — only use the data above
8. End with encouragement: "Aap yeh scheme zaroor apply karein!"
"""


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    state: Optional[str] = None
    language: Optional[str] = "hinglish"


class SchemeMatch(BaseModel):
    name: str
    sector: str
    apply_url: str
    helpline: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    language: str
    matched_schemes: List[SchemeMatch]
    session_id: str


def _get_client() -> Groq:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not configured on the server.")
    return Groq(api_key=key)


def _get_session_history(sid: str, state: str = None, lang: str = "hinglish") -> list:
    """Ensure session exists in Supabase (via Spring Boot) and return recent messages."""
    try:
        with httpx.Client(timeout=5.0) as client:
            # Create or get session
            client.post(f"{SPRING_URL}/api/internal/chat/session", json={
                "sessionId": sid,
                "language": lang,
                "state": state,
                "sessionType": "CHAT"
            })
            # Fetch last 12 messages
            resp = client.get(f"{SPRING_URL}/api/internal/chat/session/{sid}/history", params={"limit": 12})
            if resp.status_code == 200:
                data = resp.json()
                return [{"role": m["role"], "content": m["content"]} for m in data.get("messages", [])]
    except Exception as e:
        logger.warning(f"Spring Boot session fetch failed, continuing with empty history: {e}")
    return []


def _save_message(sid: str, role: str, content: str, schemes_mentioned: list = None):
    """Persist a message to Supabase via Spring Boot internal API."""
    try:
        schemes_json = json.dumps(schemes_mentioned) if schemes_mentioned else None
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{SPRING_URL}/api/internal/chat/message", json={
                "sessionId": sid,
                "role": role,
                "content": content,
                "schemesMentioned": schemes_json
            })
    except Exception as e:
        logger.warning(f"Failed to save message to Supabase: {e}")


def _find_mentioned_schemes(reply: str) -> List[SchemeMatch]:
    mentioned = []
    reply_lower = reply.lower()
    for s in _SCHEMES_DATA:
        if s["name"].lower() in reply_lower or s["key"] in reply_lower:
            mentioned.append(SchemeMatch(
                name=s["name"],
                sector=s["sector"],
                apply_url=s["apply_url"],
                helpline=s.get("helpline"),
            ))
    return mentioned[:3]


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        client = _get_client()
        sid = req.session_id or "default"
        history = _get_session_history(sid, req.state, req.language)

        user_content = req.message
        if req.state:
            user_content = f"[User's state: {req.state}] {req.message}"

        _save_message(sid, "user", user_content)
        history.append({"role": "user", "content": user_content})

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + history[-12:]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )
        reply = completion.choices[0].message.content

        matches = _find_mentioned_schemes(reply)
        m_list = [m.name for m in matches]
        _save_message(sid, "assistant", reply, m_list)

        return ChatResponse(
            reply=reply,
            language=req.language or "hinglish",
            matched_schemes=matches,
            session_id=sid,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI service error: {e}")


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        client = _get_client()
        sid = req.session_id or "default"
        history = _get_session_history(sid, req.state, req.language)

        user_content = req.message
        if req.state:
            user_content = f"[User's state: {req.state}] {req.message}"

        _save_message(sid, "user", user_content)
        history.append({"role": "user", "content": user_content})

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + history[-12:]

        def generate():
            full = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=400,
                stream=True,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                full += token
                yield token

            matches = _find_mentioned_schemes(full)
            m_list = [m.name for m in matches]
            _save_message(sid, "assistant", full, m_list)

        return StreamingResponse(generate(), media_type="text/plain")
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    try:
        with httpx.Client(timeout=5.0) as client:
            client.delete(f"{SPRING_URL}/api/internal/chat/session/{session_id}")
    except Exception as e:
        logger.warning(f"Failed to clear session in Supabase: {e}")
    return {"status": "cleared", "session_id": session_id}


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve chat history for a given session from Supabase."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{SPRING_URL}/api/internal/chat/session/{session_id}/history", params={"limit": 50})
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch session history: {e}")
    return {"session_id": session_id, "messages": []}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "groq_chat_supabase"}
