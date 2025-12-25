import easyocr
import re
import numpy as np
from PIL import Image

reader = easyocr.Reader(['en'], gpu=False)

CBC_TESTS = {
    "Hemoglobin": (13.0, 17.0),
    "RBC": (4.5, 5.5),
    "PCV": (40, 50),
    "MCV": (83, 101),
    "MCH": (27, 32),
    "MCHC": (31.5, 34.5),
    "RDW-SD": (39, 46),
    "RDW-CV": (11.6, 14.0),
    "Total Leucocyte Count": (4, 10),
    "Platelet Count": (150, 410),
}

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    ocr_results = reader.readtext(image_np, detail=0)

    text = "\n".join(ocr_results)

    extracted = []

    for test, (low, high) in CBC_TESTS.items():
        pattern = rf"{test}.*?([\d\.]+)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = float(match.group(1))
            status = "Normal" if low <= value <= high else "Abnormal"

            extracted.append({
                "Test": test,
                "Value": value,
                "Normal Range": f"{low} - {high}",
                "Status": status
            })

    return extracted
