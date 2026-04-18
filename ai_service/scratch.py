import numpy as np
import traceback
from paddleocr import PaddleOCR
try:
    ocr = PaddleOCR(use_angle_cls=True, lang="en", enable_mkldnn=False, ocr_version="PP-OCRv4")
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    res = ocr.ocr(img)
    print("SUCCESS V4!!")
except Exception as e:
    traceback.print_exc()
