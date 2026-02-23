"""PII Masker utility — masks Aadhaar and PAN before sending to AI"""
import re

AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')
PAN_PATTERN     = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
PHONE_PATTERN   = re.compile(r'\b[6-9]\d{9}\b')

def mask_pii(text: str) -> tuple[str, list[str]]:
    """
    Masks Aadhaar, PAN, and phone numbers in text.
    Returns (masked_text, list_of_detected_pii_types)
    """
    detected = []
    if AADHAAR_PATTERN.search(text):
        text = AADHAAR_PATTERN.sub("XXXX-XXXX-XXXX", text)
        detected.append("aadhaar")
    if PAN_PATTERN.search(text):
        text = PAN_PATTERN.sub("XXXXXXXXXX", text)
        detected.append("pan")
    if PHONE_PATTERN.search(text):
        text = PHONE_PATTERN.sub("XXXXXXXXXX", text)
        detected.append("phone")
    return text, detected


# ── Test ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        "Mera Aadhaar 9876 5432 1234 hai",
        "PAN card ABCDE1234F chahiye",
        "Mere phone pe call karo 9876543210",
        "PM Kisan ke liye apply karna hai",
    ]
    for s in samples:
        masked, pii = mask_pii(s)
        print(f"Original : {s}")
        print(f"Masked   : {masked}  [detected: {pii}]")
        print()
