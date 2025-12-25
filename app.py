import streamlit as st
import easyocr
import numpy as np
import pandas as pd
import re
from PIL import Image
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Lab Report Digitizer",
    page_icon="🧪",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
}
.block-container {
    background: rgba(255,255,255,0.95);
    border-radius: 16px;
    padding: 25px;
}
h1, h2, h3 {
    color: #0f2027;
}
</style>
""", unsafe_allow_html=True)

# ---------------- OCR ----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

def ocr_image(img):
    results = reader.readtext(np.array(img))
    return " ".join([r[1] for r in results])

# ---------------- TEST RANGES ----------------
TESTS = {
    "Hemoglobin": (13, 17),
    "WBC": (4000, 11000),
    "Platelets": (150000, 450000),
    "RBC": (4.5, 5.9),
    "Blood Sugar": (70, 140),
    "Cholesterol": (125, 200),
    "Creatinine": (0.6, 1.3)
}

# ---------------- EXTRACT VALUES ----------------
def extract_values(text):
    data = []
    for test, (low, high) in TESTS.items():
        match = re.search(fr"{test}[^0-9]*([\d.]+)", text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            status = "Normal"
            color = "🟢"
            if value < low:
                status = "Low"
                color = "🔴"
            elif value > high:
                status = "High"
                color = "🔴"

            data.append([test, value, low, high, f"{color} {status}"])
    return pd.DataFrame(data, columns=["Test", "Value", "Low", "High", "Status"])

# ---------------- PDF ----------------
def create_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = [Paragraph("AI Digitized Lab Report", styles["Title"])]
    table_data = [df.columns.tolist()] + df.values.tolist()
    content.append(Table(table_data))
    doc.build(content)

    buffer.seek(0)
    return buffer

# ---------------- UI ----------------
st.title("🧪 AI Lab Report Digitizer")
st.write("Upload a **medical lab report image** and get instant digital results.")

uploaded = st.file_uploader("📤 Upload Lab Report Image", type=["png","jpg","jpeg"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Report", use_column_width=True)

    with st.spinner("🔍 Reading report..."):
        text = ocr_image(image)

    st.subheader("📝 OCR Extracted Text")
    st.text_area("Detected Text", text, height=150)

    df = extract_values(text)

    if not df.empty:
        st.subheader("📊 Digitized Results")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", csv, "lab_report.csv", "text/csv")

        with col2:
            pdf = create_pdf(df)
            st.download_button("⬇ Download PDF", pdf, "lab_report.pdf", "application/pdf")

    else:
        st.error("❌ No lab values detected. Try a clearer image.")

st.markdown("---")
st.caption("© AI Lab Report Digitizer | EasyOCR Powered")
