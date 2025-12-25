import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import re

st.set_page_config(page_title="CBC Lab Report Analyzer", layout="wide")

st.title("🧪 Medical Lab Report Analyzer (CBC)")
st.write("Upload a **clear CBC lab report image (PNG/JPG)**")

uploaded_file = st.file_uploader(
    "Upload Lab Report Image",
    type=["png", "jpg", "jpeg"]
)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    return gray

def extract_text(img):
    results = reader.readtext(img, detail=0, paragraph=True)
    return "\n".join(results)

def parse_cbc(text):
    patterns = {
        "Hemoglobin (g/dL)": r"Haemoglobin|Hemoglobin.*?(\d+\.?\d*)",
        "Total WBC (/cumm)": r"Total.*?(Leuco|WBC).*?(\d{3,6})",
        "Platelet Count (/cumm)": r"Platelet.*?(\d{5,7})",
        "RBC (million/cumm)": r"RBC.*?(\d+\.?\d*)",
        "MCV (fL)": r"MCV.*?(\d+\.?\d*)",
        "MCH (pg)": r"MCH.*?(\d+\.?\d*)",
        "MCHC (g/dL)": r"MCHC.*?(\d+\.?\d*)"
    }

    extracted = {}
    for test, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[test] = match.groups()[-1]

    return extracted

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded CBC Report", use_column_width=True)

    img_np = np.array(image)
    processed = preprocess(img_np)

    with st.spinner("🔍 Reading report using EasyOCR..."):
        ocr_text = extract_text(processed)
        cbc_data = parse_cbc(ocr_text)

    st.subheader("🧾 OCR Extracted Text (Debug)")
    with st.expander("Show OCR text"):
        st.text(ocr_text)

    if cbc_data:
        st.success("✅ CBC values detected successfully")

        df = pd.DataFrame(
            cbc_data.items(),
            columns=["Test", "Value"]
        )

        st.subheader("📊 Extracted CBC Results")
        st.table(df)

    else:
        st.error("❌ Unable to detect CBC values. Please upload a clearer image.")
