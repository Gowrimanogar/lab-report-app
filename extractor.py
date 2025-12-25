import easyocr
import numpy as np
import cv2
import re

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(uploaded_file):
    # Convert uploaded file to bytes
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)

    # Decode image using OpenCV
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # OCR
    results = reader.readtext(image)

    # Combine detected text
    text = " ".join([res[1] for res in results])

    return text


def detect_tests(text):
    tests = {}

    patterns = {
        "Hemoglobin": (r"hemoglobin\s*[:\-]?\s*(\d+\.?\d*)", 13, 17),
        "Glucose": (r"glucose\s*[:\-]?\s*(\d+\.?\d*)", 70, 110),
        "Cholesterol": (r"cholesterol\s*[:\-]?\s*(\d+\.?\d*)", 125, 200),
        "Platelets": (r"platelets\s*[:\-]?\s*(\d+\.?\d*)", 150000, 450000),
    }

    for test, (pattern, low, high) in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            status = "Normal" if low <= value <= high else "Abnormal"
            tests[test] = {
                "value": value,
                "low": low,
                "high": high,
                "status": status
            }

    return tests
