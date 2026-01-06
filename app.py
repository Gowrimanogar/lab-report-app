import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import pandas as pd
import re
from pyzbar.pyzbar import decode

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Lab Report Digitizer",
    page_icon="🧪",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    padding: 2rem;
}
h1, h2, h3, p {
    color: white;
}
.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("""
<div class="card">
<h1>🧪 AI Lab Report Digitizer</h1>
<p>Upload medical report or QR / Barcode image</p>
</div>
""", unsafe_allow_html=True)

# ---------------- OCR READER ----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# ---------------- CBC NORMAL RANGES ----------------
CBC_RANGES = {
    "Hemoglobin": (13.0, 17.0, "g/dL"),
    "RBC": (4.5, 5.5, "million/cu.mm"),
    "PCV": (40, 50, "%"),
    "MCV": (83, 101, "fL"),
    "MCH": (27, 32, "pg"),
    "MCHC": (31.5, 34.5, "g/dL"),
    "RDW-CV": (11.6, 14.0, "%"),
    "Total Leucocyte Count": (4.0, 10.0, "10³/µL"),
    "Platelet Count": (150, 410, "10³/µL"),
    "Neutrophils": (40, 80, "%"),
    "Lymphocytes": (20, 40, "%"),
    "Monocytes": (2, 10, "%"),
    "Eosinophils": (1, 6, "%"),
    "Basophils": (0, 2, "%"),
}

# ---------------- QR / BARCODE SCAN ----------------
def scan_qr_barcode(image):
    decoded = decode(image)
    return [d.data.decode("utf-8") for d in decoded]

# ---------------- MEDICAL VALUE EXTRACTION ----------------
def extract_tests(text):
    results = []

    for test in CBC_RANGES.keys():
        pattern = rf"{test}\s+([\d.]+)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = float(match.group(1))
            low, high, unit = CBC_RANGES[test]

            if value < low:
                status = "Low"
            elif value > high:
                status = "High"
            else:
                status = "Normal"

            results.append({
                "Test Name": test,
                "Value": value,
                "Unit": unit,
                "Normal Range": f"{low} - {high}",
                "Status": status
            })

    return pd.DataFrame(results)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Medical Report OR QR / Barcode Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    # -------- QR / BARCODE --------
    qr_data = scan_qr_barcode(image)

    if qr_data:
        st.markdown("### 📦 QR / Barcode Data")
        for item in qr_data:
            st.success(item)
    else:
        st.info("🔍 No QR found. Processing as Medical Report...")

    # -------- OCR --------
    st.markdown("### 🧾 Extracted Medical Data")

    ocr_result = reader.readtext(img_array, detail=0)
    full_text = " ".join(ocr_result)

    if full_text.strip():
        df = extract_tests(full_text)

        if not df.empty:

            # ---------- COLOR STATUS ----------
            def color_status(val):
                if val == "High":
                    return "color:red"
                elif val == "Low":
                    return "color:orange"
                else:
                    return "color:green"

            st.success("✅ Test Results Detected")
            st.dataframe(df.style.applymap(color_status, subset=["Status"]),
                         use_container_width=True)

            # ---------- CSV DOWNLOAD ----------
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download CSV",
                csv,
                "lab_report.csv",
                "text/csv"
            )
        else:
            st.warning("❌ No valid blood test values detected.")
    else:
        st.warning("❌ OCR failed to read text.")
