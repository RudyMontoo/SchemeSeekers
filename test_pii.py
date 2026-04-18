from ai_service.utils.pii_masker import mask_pii

text = "My Aadhaar is 1234 5678 9012 and PAN is ABCDE1234F. My phone is +91-9876543210."
masked = mask_pii(text)
print("Original:", text)
print("Masked:", masked)

