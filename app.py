import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="Lab Report Digitizer", layout="centered")
st.title("🧪 Lab Report Digitizer")

# -------------------------------
# Load OCR model once
# -------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# -------------------------------
# OCR function (cached)
# -------------------------------
@st.cache_data
def ocr_image(_image):
    result = reader.readtext(np.array(_image))
    return " ".join([r[1] for r in result])

# -------------------------------
# Upload image
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Lab Report Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # OCR
    text = ocr_image(image)

    st.subheader("📄 OCR Output")
    st.write(text)

    # -------------------------------
    # Extract values
    # -------------------------------
    st.subheader("📊 Digitized Values")

    words = text.replace(":", " ").split()
    params = {}

    i = 0
    while i < len(words) - 1:
        try:
            word = words[i].lower()

            if word == "hemoglobin":
                value = float(words[i + 1])
                status = "Normal" if 12 <= value <= 16 else "Abnormal"
                params["Hemoglobin"] = f"{value} → {status}"
                i += 2

            elif word == "blood" and words[i + 1].lower() == "sugar":
                value = float(words[i + 2])
                status = "Normal" if 70 <= value <= 140 else "Abnormal"
                params["Blood Sugar"] = f"{value} → {status}"
                i += 3

            elif word == "cholesterol":
                value = float(words[i + 1])
                status = "Normal" if value < 200 else "Abnormal"
                params["Cholesterol"] = f"{value} → {status}"
                i += 2

            else:
                i += 1

        except:
            i += 1

    if params:
        for k, v in params.items():
            st.write(f"**{k}:** {v}")

        df = pd.DataFrame(params.items(), columns=["Parameter", "Result"])
        df.to_csv("patient_data.csv", index=False)

        st.success("✅ Data extracted successfully")
    else:
        st.warning("⚠️ No parameters found")

else:
    st.info("👆 Please upload a lab report image")
