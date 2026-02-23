"""
Main FastAPI entrypoint — Yojna Setu AI Service
Runs on: http://localhost:8000
Docs:    http://localhost:8000/docs
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env from ai_service directory explicitly
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Yojna Setu AI Service",
    description="AI/ML backend for Yojna Setu — Indian Government Scheme Assistant",
    version="1.0.0",
)

# ── CORS (allow React frontend on port 3000 and Spring Boot on 8080) ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ─────────────────────────────────────────────────────────────
from ai_service.routers.chat import router as chat_router
from ai_service.routers.status_tracker import router as status_router
from ai_service.routers.agent_router import router as agent_router
from ai_service.routers.voice import router as voice_router
from ai_service.routers.voice_conversation import router as voice_conv_router

app.include_router(chat_router)
app.include_router(status_router, prefix="/status")
app.include_router(agent_router)
app.include_router(voice_router)
app.include_router(voice_conv_router)

# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "Yojna Setu AI",
        "version": "1.0.0",
        "endpoints": {
            "chat":           "/chat — RAG-powered scheme chatbot",
            "agent":          "/agent/start + /agent/answer — Adaptive interview",
            "voice":          "/voice/transcribe + /voice/query — Whisper STT",
            "status_tracker": "/status/check — Live scheme application status",
            "docs":           "/docs",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Dev server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_service.main:app", host="0.0.0.0", port=8000, reload=True)
