import streamlit as st
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
from fpdf import FPDF
import re
import io

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Lab Report Digitizer",
    page_icon="🧪",
    layout="wide"
)

# -------------------- BACKGROUND & UI DESIGN --------------------
st.markdown("""
<style>
body {
    background-image: url("https://images.unsplash.com/photo-1581090700227-1e37b190418e");
    background-size: cover;
}

.main {
    background: rgba(0,0,0,0.75);
    padding: 25px;
    border-radius: 15px;
}

h1, h2, h3, label {
    color: #ffffff !important;
}

.stButton>button {
    background-color: #00c6ff;
    color: black;
    border-radius: 10px;
    font-size: 16px;
}

.dataframe {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.markdown("""
<div class="main">
<h1>🧪 Lab Report Digitizer</h1>
<p style="color:#cfd8dc;">Convert medical lab report images into structured digital analytics</p>
</div>
""", unsafe_allow_html=True)

# -------------------- CACHE OCR READER --------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# -------------------- CACHE IMAGE PROCESS --------------------
@st.cache_data(show_spinner=False)
def extract_text(image_array):
    result = reader.readtext(image_array)
    return " ".join([res[1] for res in result])

# -------------------- AUTO TEST DETECTION --------------------
def detect_tests(text):
    patterns = {
        "Hemoglobin (g/dL)": r"(hemoglobin|hb)\s*[:\-]?\s*(\d+\.?\d*)",
        "Blood Sugar (mg/dL)": r"(blood sugar|glucose)\s*[:\-]?\s*(\d+)",
        "Cholesterol (mg/dL)": r"(cholesterol)\s*[:\-]?\s*(\d+)",
        "WBC Count": r"(wbc)\s*[:\-]?\s*(\d+\.?\d*)",
        "Platelets": r"(platelet)\s*[:\-]?\s*(\d+)",
        "RBC Count": r"(rbc)\s*[:\-]?\s*(\d+\.?\d*)",
        "Creatinine (mg/dL)": r"(creatinine)\s*[:\-]?\s*(\d+\.?\d*)",
        "Urea (mg/dL)": r"(urea)\s*[:\-]?\s*(\d+)",
        "SGPT (ALT)": r"(sgpt|alt)\s*[:\-]?\s*(\d+)",
        "SGOT (AST)": r"(sgot|ast)\s*[:\-]?\s*(\d+)",
    }

    data = []
    for test, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data.append([test, match.group(2)])

    return pd.DataFrame(data, columns=["Test Name", "Value"])

# -------------------- PDF GENERATOR --------------------
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Digitized Lab Report", ln=True)

    for _, row in df.iterrows():
        pdf.cell(0, 10, f"{row['Test Name']}: {row['Value']}", ln=True)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes

# -------------------- FILE UPLOAD --------------------
st.markdown("## 📤 Upload Lab Report Image")
uploaded_file = st.file_uploader(
    "Upload medical report image (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

# -------------------- MAIN PROCESS --------------------
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Medical Report", use_column_width=True)

    img_array = np.array(image)

    with st.spinner("🔍 Extracting medical data..."):
        extracted_text = extract_text(img_array)

    st.markdown("### 🧾 Extracted Text")
    st.text_area("", extracted_text, height=150)

    df = detect_tests(extracted_text)

    if not df.empty:
        st.markdown("### 📊 Auto-Detected Test Results")
        st.dataframe(df, use_container_width=True)

        # Chart
        st.markdown("### 📈 Test Value Analytics")
        chart_df = df.copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
        st.bar_chart(chart_df.set_index("Test Name"))

        # PDF Download
        pdf_data = generate_pdf(df)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name="Lab_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ No recognizable medical tests found")

# -------------------- FOOTER --------------------
st.markdown("""
<hr>
<p style="color:#90caf9; text-align:center;">
AI-Powered Medical Report Digitization | Streamlit + EasyOCR
</p>
""", unsafe_allow_html=True)
