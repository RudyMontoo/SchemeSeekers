"""
pii_masker.py — PII auto-masking utility
Masks Aadhaar, PAN, phone numbers, and email addresses
before logging or returning in AI responses.
"""
import re

# Patterns
_AADHAAR = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')
_PAN     = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')
_PHONE   = re.compile(r'\b(?:\+91[\s\-]?)?[6-9]\d{9}\b')
_EMAIL   = re.compile(r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b')


def mask_pii(text: str) -> str:
    """Return text with sensitive data replaced by masked equivalents."""
    if not text:
        return text
    text = _AADHAAR.sub('XXXX-XXXX-XXXX', text)
    text = _PAN.sub('XXXXX****X', text)
    text = _PHONE.sub('+91-XXXXXX-XXXX', text)
    text = _EMAIL.sub('user@****.***', text)
    return text


def mask_request_body(body: dict) -> dict:
    """Recursively mask PII in a JSON-like dict for safe logging."""
    masked = {}
    for k, v in body.items():
        if isinstance(v, str):
            masked[k] = mask_pii(v)
        elif isinstance(v, dict):
            masked[k] = mask_request_body(v)
        elif isinstance(v, list):
            masked[k] = [mask_pii(i) if isinstance(i, str) else i for i in v]
        else:
            masked[k] = v
    return masked
