import streamlit as st
import numpy as np
import pandas as pd
import easyocr
import re
from PIL import Image
from io import BytesIO

# ================== APP CONFIG ==================
st.set_page_config(
    page_title="Medical Lab Report Analyzer",
    page_icon="🧪",
    layout="wide"
)

# ================== STYLING ==================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.block-container {
    padding: 2rem;
}
.card {
    background-color: #0f172a;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
}
.green { color:#22c55e; font-weight:700; }
.red { color:#ef4444; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ================== OCR ==================
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()

def ocr_image(image):
    results = reader.readtext(np.array(image), detail=0)
    return " ".join(results)

# ================== TEST RULES ==================
TESTS = {
    "Hemoglobin (g/dL)": (r"(hemoglobin|hb|hgb)\s*[:\-]?\s*(\d+\.?\d*)", 13, 17),
    "RBC (million/uL)": (r"\brbc\b\s*[:\-]?\s*(\d+\.?\d*)", 4.5, 6.0),
    "WBC (cells/uL)": (r"(wbc|tlc|total leucocyte count)\s*[:\-]?\s*(\d+)", 4000, 11000),
    "Platelets (cells/uL)": (r"(platelet|plt)\s*[:\-]?\s*(\d+)", 150000, 450000),
    "PCV (%)": (r"(pcv|hct)\s*[:\-]?\s*(\d+\.?\d*)", 40, 54),
    "MCV (fL)": (r"\bmcv\b\s*[:\-]?\s*(\d+\.?\d*)", 80, 100),
    "MCH (pg)": (r"\bmch\b\s*[:\-]?\s*(\d+\.?\d*)", 27, 33),
    "MCHC (g/dL)": (r"\bmchc\b\s*[:\-]?\s*(\d+\.?\d*)", 32, 36),
}

def extract_tests(text):
    rows = []
    clean = text.lower().replace(",", "")

    for test, (pattern, low, high) in TESTS.items():
        match = re.search(pattern, clean)
        if match:
            value = float(match.group(2))
            status = "Normal" if low <= value <= high else "Abnormal"
            rows.append([test, value, f"{low}-{high}", status])

    return pd.DataFrame(rows, columns=["Test", "Value", "Normal Range", "Status"])

# ================== UI ==================
st.markdown("""
<div class="card">
<h1>🧪 Medical Lab Report Analyzer</h1>
<p>Upload your lab report image → View all detected results instantly</p>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload Lab Report (PNG / JPG)",
    type=["png","jpg","jpeg"]
)

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Report", use_column_width=True)

    with st.spinner("🔍 Extracting test results..."):
        text = ocr_image(image)

    st.subheader("📄 OCR Extracted Text")
    st.text_area("", text, height=220)

    df = extract_tests(text)

    if df.empty:
        st.error("❌ No lab test values detected. Try a clearer image.")
    else:
        st.subheader("📊 All Detected Test Results")

        def color_status(val):
            return "color: green" if val == "Normal" else "color: red"

        st.dataframe(df.style.applymap(color_status, subset=["Status"]))

        st.subheader("⬇️ Download Reports")

        # CSV
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "lab_report.csv", "text/csv")

        # PDF
        from reportlab.platypus import SimpleDocTemplate, Table
        from reportlab.lib.pagesizes import A4

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        table_data = [df.columns.tolist()] + df.values.tolist()
        doc.build([Table(table_data)])

        st.download_button(
            "📄 Download PDF",
            pdf_buffer.getvalue(),
            "lab_report.pdf",
            "application/pdf"
        )

st.markdown("""
<hr>
<center>
<small>⚠️ Educational tool only. Please consult a medical professional.</small>
</center>
""", unsafe_allow_html=True)
