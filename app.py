import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="Lab Report Digitizer", layout="centered")

st.title("🧪 Lab Report Digitization App")
st.write("Upload a lab report image to extract health parameters")

# -------------------------------
# Load OCR model (cached)
# -------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# -------------------------------
# OCR function (cached correctly)
# -------------------------------
@st.cache_data
def ocr_image(_image):
    result = reader.readtext(np.array(_image))
    text = " ".join([r[1] for r in result])
    return text

# -------------------------------
# File uploader
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Lab Report Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # -------------------------------
    # Show image
    # -------------------------------
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # -------------------------------
    # OCR
    # -------------------------------
    text = ocr_image(image)

    st.subheader("📄 OCR Output")
    st.write(text)

    # -------------------------------
    # Digitization Logic
    # -------------------------------
    st.subheader("📊 Digitized Values")

    words = text.replace(":", " ").split()
    params = {}

    i = 0
    while i < len(words) - 1:
        word = words[i].lower()

        try:
            # Hemoglobin
            if word == "hemoglobin":
                value = float(words[i + 1])
                status = "Normal" if 12 <= value <= 16 else "Abnormal"
                params["Hemoglobin"] = f"{value} → {status}"
                i += 2

            # Blood Sugar
            elif word == "blood" and words[i + 1].lower() == "sugar":
                value = float(words[i + 2])
                status = "Normal" if
