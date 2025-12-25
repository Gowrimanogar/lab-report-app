import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Lab Report Analyzer", layout="wide")
st.title("🧪 Medical Lab Report Analyzer (CBC)")

# -------------------- CBC TEST MASTER --------------------
CBC_TESTS = {
    "haemoglobin": (13, 17),
    "hemoglobin": (13, 17),
    "total leucocyte count": (4000, 10000),
    "neutrophils": (40, 80),
    "lymphocytes": (20, 40),
    "eosinophils": (1, 6),
    "monocytes": (2, 10),
    "basophils": (0, 1),
    "rbc count": (4.5, 5.5),
    "mcv": (81, 101),
    "mch": (27, 32),
    "mchc": (31.5, 34.5),
    "rdw-cv": (11.6, 14.0),
    "rdw sd": (39, 46),
    "platelet count": (150000, 410000),
    "mpv": (7.5, 11.5),
    "pdw": (9, 17)
}

# -------------------- TEXT CLEANER --------------------
def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ")
    text = text.replace("/cumm", "")
    text = text.replace("/cu.mm", "")
    text = text.replace("%", "")
    text = text.replace(":", "")
    text = re.sub(r"\s+", " ", text)
    return text

# -------------------- CBC EXTRACTION --------------------
def extract_cbc(text):
    text = clean_text(text)
    results = []

    for test, (low, high) in CBC_TESTS.items():
        pattern = rf"{test}\s+([\d\.]+)"
        match = re.search(pattern, text)

        if match:
            value = float(match.group(1))

            if value < low:
                status = "Low 🔵"
            elif value > high:
                status = "High 🔴"
            else:
                status = "Normal 🟢"

            results.append({
                "Test Name": test.title(),
                "Result": value,
                "Normal Range": f"{low} - {high}",
                "Status": status
            })

    return results

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader(
    "📤 Upload Lab Report Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Report", use_container_width=True)

    with st.spinner("🔍 Reading report..."):
        ocr_text = pytesseract.image_to_string(image)

    st.subheader("📄 Extracted Text")
    with st.expander("Show OCR Text"):
        st.text(ocr_text)

    extracted_data = extract_cbc(ocr_text)

    if extracted_data:
        df = pd.DataFrame(extracted_data)

        st.subheader("📊 CBC Analysis Result")
        st.dataframe(df, use_container_width=True)

        # -------------------- DOWNLOAD --------------------
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Result as CSV",
            data=csv,
            file_name="cbc_report_analysis.csv",
            mime="text/csv"
        )

    else:
        st.warning("⚠️ No CBC parameters detected. Try a clearer image.")

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("⚠️ For educational purposes only. Consult a doctor for medical advice.")
