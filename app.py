import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import re
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import red, green, black

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CBC Lab Analyzer", layout="wide")
st.title("🧪 CBC Lab Report Analyzer")
st.caption("Automatic CBC extraction + analysis")

# ---------------- LOAD OCR ----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# ---------------- PREPROCESS IMAGE ----------------
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray

# ---------------- OCR ----------------
def run_ocr(img):
    text = reader.readtext(img, detail=0)
    return [t.strip() for t in text if t.strip()]

# ---------------- CBC REFERENCE RANGES ----------------
CBC_RANGES = {
    "hemoglobin": (13, 17),
    "rbc": (4.5, 5.5),
    "wbc": (4000, 10000),
    "platelet": (150000, 410000),
    "mcv": (81, 101),
    "mch": (27, 32),
    "mchc": (31.5, 34.5),
    "rdw": (11.6, 14.0),
    "mpv": (7.5, 11.5)
}

CBC_KEYS = list(CBC_RANGES.keys())

# ---------------- CBC EXTRACTION ----------------
def extract_cbc(lines):
    data = []
    used = set()

    for i, line in enumerate(lines):
        l = line.lower()

        for test in CBC_KEYS:
            if test in l and i not in used:
                block = " ".join(lines[i:i+3])
                val = re.search(r"\d+\.?\d*", block)
                if val:
                    data.append([test.capitalize(), float(val.group())])
                    used.add(i)

    return data

# ---------------- STATUS FLAG ----------------
def flag_status(test, value):
    key = test.lower()
    if key in CBC_RANGES:
        low, high = CBC_RANGES[key]
        if value < low:
            return "🔴 Low"
        elif value > high:
            return "🔴 High"
        else:
            return "🟢 Normal"
    return "—"

# ---------------- PDF GENERATOR ----------------
def generate_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>CBC Lab Report</b>", styles["Title"]))

    table_data = [["Test", "Value", "Status"]]
    for _, r in df.iterrows():
        table_data.append([r["Test"], r["Value"], r["Status"]])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- FILE UPLOAD ----------------
uploaded = st.file_uploader("Upload CBC Report Image (PNG/JPG)", type=["png","jpg","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_column_width=True)

    img_np = np.array(img)
    processed = preprocess(img_np)

    with st.spinner("🔍 Extracting CBC values..."):
        lines = run_ocr(processed)
        cbc = extract_cbc(lines)

    # DEBUG TEXT
    with st.expander("🔎 OCR Debug Text"):
        for l in lines:
            st.write(l)

    if cbc:
        df = pd.DataFrame(cbc, columns=["Test", "Value"])
        df["Status"] = df.apply(lambda x: flag_status(x["Test"], x["Value"]), axis=1)

        st.success(f"✅ {len(df)} CBC parameters detected")

        # COLOR DISPLAY
        def color_row(val):
            if "High" in val or "Low" in val:
                return "color:red;font-weight:bold"
            if "Normal" in val:
                return "color:green;font-weight:bold"
            return ""

        st.dataframe(df.style.applymap(color_row, subset=["Status"]), use_container_width=True)

        # ANALYTICS
        st.subheader("📊 Analytics")
        st.bar_chart(df.set_index("Test")["Value"])

        # DOWNLOADS
        st.subheader("⬇ Downloads")

        csv = df.to_csv(index=False).encode()
        st.download_button("📄 Download CSV", csv, "cbc_report.csv", "text/csv")

        pdf = generate_pdf(df)
        st.download_button("📄 Download PDF", pdf, "cbc_report.pdf", "application/pdf")

    else:
        st.error("❌ No CBC values detected. Please upload a clearer CBC table image.")
