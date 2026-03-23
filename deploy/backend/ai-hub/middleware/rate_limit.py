"""
rate_limit.py — per backend-patterns: Simple In-Memory Rate Limiter
Tracks per-IP request counts in a sliding window.
Default: 20 req / 60s per IP (adjustable).
"""
import time
import logging
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests  = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, identifier: str) -> bool:
        """Returns True if allowed, False if rate-limited."""
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._store[identifier]
            # Drop timestamps outside the window
            self._store[identifier] = [t for t in hits if t > cutoff]
            if len(self._store[identifier]) >= self.max_requests:
                return False
            self._store[identifier].append(now)
            return True

    def remaining(self, identifier: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            return max(0, self.max_requests - len([t for t in self._store[identifier] if t > cutoff]))


# Global limiter instance
_limiter = RateLimiter(max_requests=20, window_seconds=60)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit_check(request: Request) -> None:
    """FastAPI dependency — raises 429 if rate limited."""
    ip = get_client_ip(request)
    if not _limiter.check(ip):
        remaining_secs = _limiter.window_seconds
        logger.warning(f"Rate limit exceeded: {ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests — please wait {remaining_secs} seconds",
            headers={"Retry-After": str(remaining_secs), "X-RateLimit-Limit": str(_limiter.max_requests)},
        )
