import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Lab Report Digitizer", layout="centered")

st.title("🧪 Lab Report Digitizer")

# ---------- CACHE OCR ----------
@st.cache_data(show_spinner="Extracting text...")
def ocr_image(image):
    return pytesseract.image_to_string(image)

# ---------- RANGE CHECK ----------
def check_status(test, value):
    if test == "Hemoglobin":
        return "Normal" if 12 <= value <= 16 else "Abnormal"
    if test == "Blood Sugar":
        return "Normal" if 70 <= value <= 110 else "Abnormal"
    if test == "Cholesterol":
        return "Normal" if value < 200 else "Abnormal"
    return "Unknown"

# ---------- EXTRACT VALUES ----------
@st.cache_data
def extract_values(text):
    data = []

    patterns = {
        "Hemoglobin": r'Hemoglobin\s*(\d+\.?\d*)',
        "Blood Sugar": r'Blood Sugar\s*(\d+\.?\d*)',
        "Cholesterol": r'Cholesterol\s*(\d+\.?\d*)'
    }

    for test, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        if match:
            value = float(match.group(1))
            status = check_status(test, value)
            data.append([test, value, status])

    return pd.DataFrame(data, columns=["Test", "Value", "Status"])

# ---------- FILE UPLOADER ----------
uploaded_file = st.file_uploader(
    "Upload Lab Report Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Lab Report", use_column_width=True)

    # OCR
    text = ocr_image(image)

    st.subheader("🧾 OCR Output")
    st.write(text)

    # Table
    df = extract_values(text)

    st.subheader("📊 Digitized Lab Results")
    st.dataframe(df, use_container_width=True)

    # ---------- CSV DOWNLOAD ----------
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download CSV",
        csv,
        "lab_report.csv",
        "text/csv"
    )

    # ---------- PDF DOWNLOAD ----------
    if st.button("⬇ Download PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Lab Report Digitized Results", ln=True)
        pdf.ln(5)

        for _, row in df.iterrows():
            pdf.cell(0, 10, f"{row['Test']}: {row['Value']} → {row['Status']}", ln=True)

        pdf.output("lab_report.pdf")
        with open("lab_report.pdf", "rb") as f:
            st.download_button("📄 Click to Download PDF", f, file_name="lab_report.pdf")

# ---------- CLEAR CACHE ----------
st.divider()
if st.button("🧹 Clear Cache & Restart"):
    st.cache_data.clear()
    st.experimental_rerun()
