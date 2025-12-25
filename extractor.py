import easyocr
import numpy as np
from PIL import Image
import re

reader = easyocr.Reader(['en'], gpu=False)

CBC_KEYWORDS = [
    "Hemoglobin", "RBC", "PCV", "MCV", "MCH", "MCHC",
    "RDW", "WBC", "Platelet"
]

NORMAL_RANGES = {
    "Hemoglobin": (13.0, 17.0),
    "RBC": (4.5, 5.5),
    "PCV": (40, 50),
    "MCV": (83, 101),
    "MCH": (27, 32),
    "MCHC": (31.5, 34.5),
    "RDW": (11.6, 14.0),
    "WBC": (4.0, 10.0),
    "Platelet": (150, 410)
}

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    lines = reader.readtext(img_np, detail=0)

    extracted = []

    for line in lines:
        for test in CBC_KEYWORDS:
            if test.lower() in line.lower():
                numbers = re.findall(r"\d+\.\d+|\d+", line)
                if numbers:
                    value = float(numbers[0])
                    low, high = NORMAL_RANGES[test]

                    status = "Normal"
                    if value < low or value > high:
                        status = "Abnormal"

                    extracted.append({
                        "Test": test,
                        "Value": value,
                        "Normal Range": f"{low} - {high}",
                        "Status": status
                    })

    # Remove duplicates
    unique = {d["Test"]: d for d in extracted}
    return list(unique.values())
