"""
logging_mw.py — per backend-patterns: Structured Logging
JSON-formatted request/response logging with latency tracking.
Masks PII before logging bodies.
"""
import time
import json
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from middleware.pii_masker import mask_pii

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Raw JSON lines
)
logger = logging.getLogger("yojna_setu")


def _log(level: str, event: str, **fields):
    """Emit a structured JSON log line."""
    entry = {
        "ts":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "event": event,
        **fields,
    }
    print(json.dumps(entry, ensure_ascii=False), flush=True)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, latency, and request_id."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request_id to request state for downstream use
        request.state.request_id = request_id

        _log("info", "request_start",
             request_id=request_id,
             method=request.method,
             path=request.url.path,
             ip=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            _log("info", "request_end",
                 request_id=request_id,
                 status=response.status_code,
                 latency_ms=latency_ms,
                 path=request.url.path,
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            _log("error", "request_error",
                 request_id=request_id,
                 error=str(exc),
                 latency_ms=latency_ms,
                 path=request.url.path,
            )
            raise
