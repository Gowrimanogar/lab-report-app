import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CBC Lab Analyzer", layout="wide")
st.title("🧪 CBC Lab Report Analyzer")
st.write("Upload a clear CBC report image (PNG / JPG)")

# ---------------- OCR LOADER ----------------
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()

# ---------------- IMAGE PREPROCESS ----------------
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    return gray

# ---------------- OCR ----------------
def extract_text(img):
    result = reader.readtext(img, detail=0, paragraph=False)
    return result

# ---------------- SMART CBC PARSER ----------------
def extract_cbc_values(lines):
    cbc_data = []

    for line in lines:
        line = line.strip()

        # Pattern: TEST NAME  VALUE  UNIT
        match = re.search(
            r"([A-Za-z ()/%\-]+)\s+(\d+\.?\d*)\s*(g/dL|%|fL|pg|/cumm|million|10\^3|10\^6)?",
            line
        )

        if match:
            test = match.group(1).strip()
            value = match.group(2)
            unit = match.group(3) if match.group(3) else ""

            # Remove junk lines
            if len(test) > 3 and not test.lower().startswith("ref"):
                cbc_data.append([test, value, unit])

    return cbc_data

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload CBC Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Report", use_column_width=True)

    img_np = np.array(image)
    processed = preprocess(img_np)

    with st.spinner("🔍 Reading report using EasyOCR..."):
        ocr_lines = extract_text(processed)
        cbc_rows = extract_cbc_values(ocr_lines)

    # ---------------- DEBUG ----------------
    with st.expander("🔎 OCR Raw Text"):
        for l in ocr_lines:
            st.write(l)

    # ---------------- RESULTS ----------------
    if cbc_rows:
        df = pd.DataFrame(
            cbc_rows,
            columns=["Test Name", "Value", "Unit"]
        )

        st.success(f"✅ Detected {len(df)} CBC tests")
        st.dataframe(df, use_container_width=True)

        # ---------------- ANALYTICS ----------------
        st.subheader("📊 Analytics")
        numeric_df = df.copy()
        numeric_df["Value"] = pd.to_numeric(numeric_df["Value"], errors="coerce")

        st.bar_chart(
            numeric_df.set_index("Test Name")["Value"]
        )

    else:
        st.error("❌ No CBC values detected. Try a clearer image.")
