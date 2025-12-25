import streamlit as st
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
from fpdf import FPDF
import re
import io

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Lab Report Digitizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# HEADER WITH MEDICAL IMAGE
# -------------------------------------------------
st.markdown("""
<style>
.header-box {
    background-color: #0f172a;
    padding: 25px;
    border-radius: 12px;
}
.header-title {
    font-size: 42px;
    font-weight: bold;
    color: #ffffff;
}
.header-sub {
    color: #94a3b8;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div class="header-title">🧪 Lab Report Digitizer</div>
    <div class="header-sub">
        Convert medical lab reports into structured digital data
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------------------------------------------------
# LOAD OCR MODEL (CACHED)
# -------------------------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# -------------------------------------------------
# OCR FUNCTION (NO CACHE – IMAGE IS UNHASHABLE)
# -------------------------------------------------
def ocr_image(image):
    img_array = np.array(image)
    results = reader.readtext(img_array)
    text = " ".join([res[1] for res in results])
    return text

# -------------------------------------------------
# AUTO TEST DETECTION
# -------------------------------------------------
def extract_tests(text):
    rows = []

    # Generic pattern: TestName value
    pattern = r"([A-Za-z ]{3,25})\s*[:\-]?\s*(\d+\.?\d*)"

    matches = re.findall(pattern, text)

    for test, value in matches:
        test = test.strip().title()
        value = float(value)

        # Simple normal logic (generic)
        status = "Normal"
        if value <= 0:
            status = "Abnormal"

        rows.append([test, value, status])

    df = pd.DataFrame(rows, columns=["Test Name", "Value", "Status"])

    # Remove duplicates
    df = df.drop_duplicates(subset=["Test Name"])

    return df

# -------------------------------------------------
# PDF GENERATOR
# -------------------------------------------------
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Lab Report - Digitized Results", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", size=11)

    for _, row in df.iterrows():
        pdf.cell(
            0, 8,
            f"{row['Test Name']} : {row['Value']} ({row['Status']})",
            ln=True
        )

    return pdf.output(dest="S").encode("latin-1")

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
st.subheader("📤 Upload Lab Report Image")

uploaded_file = st.file_uploader(
    "",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.markdown("### 🖼 Uploaded Medical Report")
    st.image(image, width=500)

    with st.spinner("🔍 Performing OCR on medical report..."):
        text = ocr_image(image)

    st.markdown("### 📄 OCR Extracted Text")
    st.info(text)

    df = extract_tests(text)

    if not df.empty:
        st.markdown("### 📊 Digitized Lab Values")
        st.dataframe(df, use_container_width=True)

        st.success("✅ Medical data extracted successfully")

        # ---------------- DOWNLOAD OPTIONS ----------------
        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download CSV",
                csv,
                "lab_results.csv",
                "text/csv"
            )

        with col2:
            pdf_bytes = generate_pdf(df)
            st.download_button(
                "📄 Generate PDF",
                pdf_bytes,
                "lab_report.pdf",
                "application/pdf"
            )
    else:
        st.warning("⚠ No lab values detected in the report.")
