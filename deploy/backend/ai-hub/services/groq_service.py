"""
GroqService — per backend-patterns: Service Layer + Retry with Exponential Backoff
Wraps the Groq client with retry logic, structured error handling
"""
import os
import time
import logging
from typing import Optional
from groq import Groq, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)

_CLIENT: Optional[Groq] = None

def get_groq() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY environment variable not set")
        _CLIENT = Groq(api_key=key)
    return _CLIENT


def complete_with_retry(
    messages: list[dict],
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 900,
    temperature: float = 0.7,
    max_retries: int = 3,
) -> str:
    """
    Per backend-patterns: Retry with Exponential Backoff
    Retries on rate-limit and connection errors only.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            resp = get_groq().chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""
        except RateLimitError as e:
            last_error = e
            wait = 2 ** attempt          # 1s, 2s, 4s
            logger.warning(f"Groq rate limit — retry {attempt+1}/{max_retries} in {wait}s")
            time.sleep(wait)
        except APIConnectionError as e:
            last_error = e
            wait = 2 ** attempt
            logger.warning(f"Groq connection error — retry {attempt+1}/{max_retries} in {wait}s")
            time.sleep(wait)
        except Exception as e:
            # Non-retryable — surface immediately
            logger.error(f"Groq non-retryable error: {e}")
            raise

    logger.error(f"Groq exhausted {max_retries} retries: {last_error}")
    raise RuntimeError(f"AI service temporarily unavailable after {max_retries} retries") from last_error


def stream_with_retry(
    messages: list[dict],
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 900,
    temperature: float = 0.7,
):
    """Stream mode — no retry (streaming can't retry mid-stream)"""
    return get_groq().chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )
