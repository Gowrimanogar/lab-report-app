import streamlit as st
import easyocr
import numpy as np
import pandas as pd
import re
from PIL import Image
from fpdf import FPDF
import io

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CBC Lab Report Analyzer",
    page_icon="🧪",
    layout="wide"
)

st.markdown("""
<style>
body {background-color:#0e1117;}
h1,h2,h3,p {color:white;}
</style>
""", unsafe_allow_html=True)

st.title("🧪 CBC Lab Report Analysis")
st.caption("Upload CBC image → Extract all tests → Highlight abnormal values → Download PDF/CSV")

# ---------------- OCR ----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

def ocr_image(image):
    result = reader.readtext(np.array(image))
    return " ".join([r[1] for r in result])

# ---------------- TEST RANGES ----------------
NORMAL_RANGES = {
    "WBC": (4000, 11000),
    "RBC": (4.5, 5.9),
    "Hemoglobin": (13.5, 17.5),
    "Hematocrit": (41, 53),
    "MCV": (80, 100),
    "MCH": (27, 32),
    "MCHC": (32, 36),
    "Platelets": (150000, 450000)
}

# ---------------- EXTRACTION ----------------
def extract_tests(text):
    rows = []
    for test, (low, high) in NORMAL_RANGES.items():
        pattern = rf"{test}[^0-9]*([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            status = "Normal"
            if value < low:
                status = "Low"
            elif value > high:
                status = "High"
            rows.append([test, value, f"{low} - {high}", status])
    return pd.DataFrame(rows, columns=["Test", "Value", "Normal Range", "Status"])

# ---------------- FILE UPLOAD ----------------
uploaded = st.file_uploader("Upload CBC Report Image (PNG/JPG)", type=["png","jpg","jpeg"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Report", width=400)

    with st.spinner("Reading report..."):
        text = ocr_image(image)

    df = extract_tests(text)

    if df.empty:
        st.error("❌ No CBC values detected. Please upload a clearer image.")
    else:
        st.subheader("📋 All Detected Test Results")

        def color_status(val):
            if val == "High":
                return "color:red;font-weight:bold;"
            if val == "Low":
                return "color:orange;font-weight:bold;"
            return "color:lightgreen;font-weight:bold;"

        st.dataframe(df.style.applymap(color_status, subset=["Status"]))

        # ---------------- CSV DOWNLOAD ----------------
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "cbc_report.csv",
            "text/csv"
        )

        # ---------------- PDF DOWNLOAD ----------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "CBC Lab Report Analysis", ln=True)

        for _, row in df.iterrows():
            pdf.cell(
                200, 8,
                f"{row['Test']}: {row['Value']} ({row['Status']}) | Normal: {row['Normal Range']}",
                ln=True
            )

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "⬇ Download PDF",
            pdf_bytes,
            "cbc_report.pdf",
            "application/pdf"
        )

st.markdown("---")
st.caption("⚠ Educational use only. Always consult a medical professional.")
