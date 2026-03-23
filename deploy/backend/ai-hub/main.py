"""
Yojna Setu — FastAPI AI Hub (Deploy Version)
=============================================
Professional architecture per backend-patterns skill:
- Service layer (GroqService with retry backoff)
- Middleware: structured logging, rate limiting, PII masking
- Centralized global error handler
- Clean layered architecture
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Yojna Setu AI Hub",
    description="FastAPI AI Backend — RAG Chatbot, Agent Interview, Status Tracker, Apply Wizard",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
GATEWAY_URL  = os.getenv("GATEWAY_URL",  "http://localhost:8080")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        GATEWAY_URL,
        FRONTEND_URL,
        "https://*.vercel.app",
        "https://*.railway.app",
    ],
    allow_origin_regex=r"http://localhost:\d+",   # all localhost ports for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Structured Logging Middleware (backend-patterns: Structured Logging) ──────
from middleware.logging_mw import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
from routers.chat           import router as chat_router
from routers.agent          import router as agent_router
from routers.status_tracker import router as status_router
from routers.apply_guide    import router as apply_router
from routers.help_discovery import router as help_router
from routers.voice          import router as voice_router
from routers.analytics      import router as analytics_router

app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(status_router)
app.include_router(apply_router)
app.include_router(help_router)
app.include_router(voice_router)
app.include_router(analytics_router)


# ── Global Error Handler (backend-patterns: Centralized Error Handler) ────────
logger = logging.getLogger("yojna_setu")

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions — safe JSON response, no stack traces in prod."""
    logger.error(f"Unhandled exception [{request.method} {request.url.path}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error":   "Internal server error",
            "code":    "INTERNAL",
            "message": "Kuch galat ho gaya. Dobara try karein.",
        },
    )

@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """Handles service-layer RuntimeErrors (e.g. Groq exhausted retries)."""
    logger.warning(f"RuntimeError [{request.url.path}]: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "error":   "Service temporarily unavailable",
            "code":    "SERVICE_UNAVAILABLE",
            "message": str(exc),
        },
    )


# ── Health & Info ─────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "service": "Yojna Setu AI Hub",
        "version": "2.1.0",
        "architecture": "FastAPI + Groq Llama 3.3 70B + Service Layer",
        "endpoints": {
            "chat":    "/chat/ (POST)",
            "agent":   "/agent/start | /agent/answer (POST)",
            "status":  "/status/check (POST)",
            "apply":   "/apply/guide (GET)",
            "csc":     "/help/csc/nearby (GET)",
            "health":  "/health (GET)",
            "docs":    "/docs",
        },
    }


@app.get("/health", tags=["System"])
async def health():
    sarvam_ok = bool(os.getenv("SARVAM_API_KEY"))
    return {
        "status": "ok",
        "groq":   bool(os.getenv("GROQ_API_KEY")),
        "sarvam": sarvam_ok,
        "features": {
            "chat":           True,
            "agent":          True,
            "voice_agent":    sarvam_ok,   # Sarvam Saarika v2 STT + Bulbul v3 TTS
            "status_tracker": True,
            "apply_wizard":   True,
            "rate_limiting":  True,
            "pii_masking":    True,
            "structured_logs":True,
        },
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
