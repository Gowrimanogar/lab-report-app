import easyocr
import numpy as np
from PIL import Image
import re

reader = easyocr.Reader(['en'], gpu=False)

NORMAL_RANGES = {
    "Hemoglobin": (13, 17),
    "WBC": (4000, 11000),
    "Platelets": (150000, 450000),
    "RBC": (4.5, 5.9),
    "Glucose": (70, 140)
}

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    results = reader.readtext(image_np, detail=0)
    text = "\n".join(results)

    extracted = []

    for test, (low, high) in NORMAL_RANGES.items():
        match = re.search(rf"{test}\s*[:\-]?\s*(\d+\.?\d*)", text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            status = "Normal" if low <= value <= high else "Abnormal"

            extracted.append({
                "Test": test,
                "Value": value,
                "Low": low,
                "High": high,
                "Status": status
            })

    return extracted
