import streamlit as st
import numpy as np
import pandas as pd
import easyocr
import re
from PIL import Image
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CBC Lab Report Analyzer",
    page_icon="🧪",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.block-container {
    padding: 2rem;
}
.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
.green { color:#22c55e; font-weight:bold; }
.red { color:#ef4444; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# ---------------- OCR ----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

def ocr_image(image):
    result = reader.readtext(np.array(image), detail=0)
    return " ".join(result)

# ---------------- CBC PATTERNS ----------------
CBC_RULES = {
    "Hemoglobin (g/dL)": (r"(hemoglobin|hb|hgb)\s*[:\-]?\s*(\d+\.?\d*)", 13, 17),
    "RBC (million/uL)": (r"(rbc)\s*[:\-]?\s*(\d+\.?\d*)", 4.5, 6.0),
    "WBC (cells/uL)": (r"(wbc|tlc|total leucocyte count)\s*[:\-]?\s*(\d+\.?\d*)", 4000, 11000),
    "Platelets (cells/uL)": (r"(platelet|plt)\s*[:\-]?\s*(\d+\.?\d*)", 150000, 450000),
    "PCV (%)": (r"(pcv|hct)\s*[:\-]?\s*(\d+\.?\d*)", 40, 54),
    "MCV (fL)": (r"(mcv)\s*[:\-]?\s*(\d+\.?\d*)", 80, 100),
    "MCH (pg)": (r"(mch)\s*[:\-]?\s*(\d+\.?\d*)", 27, 33),
    "MCHC (g/dL)": (r"(mchc)\s*[:\-]?\s*(\d+\.?\d*)", 32, 36),
}

def extract_cbc(text):
    rows = []
    text = text.lower().replace(",", "")
    for test, (pattern, low, high) in CBC_RULES.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(2))
            status = "Normal" if low <= value <= high else "Abnormal"
            rows.append([test, value, f"{low}-{high}", status])
    return pd.DataFrame(rows, columns=["Test", "Value", "Normal Range", "Status"])

# ---------------- HEADER ----------------
st.markdown("""
<div class="card">
<h1>🧪 CBC Lab Report Analysis</h1>
<p>Upload CBC image → Get instant medical insights</p>
</div>
""", unsafe_allow_html=True)

# ---------------- UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Medical Report (PNG / JPG)",
    type=["png","jpg","jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Report", use_column_width=True)

    with st.spinner("🔍 Reading report..."):
        text = ocr_image(image)

    st.subheader("📄 OCR Extracted Text")
    st.text_area("", text, height=200)

    df = extract_cbc(text)

    if len(df) == 0:
        st.error("❌ No CBC values detected. Try a clearer image.")
    else:
        st.subheader("📊 CBC Results")

        def color_status(val):
            return "color: green" if val == "Normal" else "color: red"

        st.dataframe(df.style.applymap(color_status, subset=["Status"]))

        # ---------------- DOWNLOADS ----------------
        st.subheader("⬇️ Download Report")

        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "cbc_report.csv", "text/csv")

        # Simple PDF
        pdf_buffer = BytesIO()
        from reportlab.platypus import SimpleDocTemplate, Table
        from reportlab.lib.pagesizes import A4

        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        table_data = [df.columns.tolist()] + df.values.tolist()
        table = Table(table_data)
        doc.build([table])

        st.download_button(
            "📄 Download PDF",
            pdf_buffer.getvalue(),
            "cbc_report.pdf",
            "application/pdf"
        )

# ---------------- FOOTER ----------------
st.markdown("""
<hr>
<center>
<small>⚠️ This tool is for educational purposes only. Consult a doctor for medical decisions.</small>
</center>
""", unsafe_allow_html=True)
