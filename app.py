import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd
import re

# -----------------------------
# Initialize EasyOCR
# -----------------------------
reader = easyocr.Reader(['en'])

st.title("Lab Report Digitizer")

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader("Upload Lab Report Image", type=["png","jpg","jpeg"])

if uploaded_file:
    # Display uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Perform OCR
    result = reader.readtext(np.array(img))
    text = " ".join([r[1] for r in result])

    st.subheader("OCR Output")
    st.write(text)

    # -----------------------------
    # Extract Key Lab Parameters
    # -----------------------------
    params = {}

    # Hemoglobin
    match = re.search(r"Hemoglobin\s*([\d.]+)", text, re.IGNORECASE)
    params['Hemoglobin'] = f"{float(match.group(1))} --> {'Normal' if 12 <= float(match.group(1)) <= 16 else 'Abnormal'}" if match else "Not Found"

    # Blood Sugar (also check for "Glucose")
    match = re.search(r"(Blood Sugar|Glucose)\s*([\d.]+)", text, re.IGNORECASE)
    params['Blood Sugar'] = f"{float(match.group(2))} --> {'Normal' if 70 <= float(match.group(2)) <= 140 else 'Abnormal'}" if match else "Not Found"

    # Cholesterol
    match = re.search(r"Cholesterol\s*([\d.]+)", text, re.IGNORECASE)
    params['Cholesterol'] = f"{float(match.group(1))} --> {'Normal' if float(match.group(1)) < 200 else 'Abnormal'}" if match else "Not Found"

    # -----------------------------
    # Display extracted values
    # -----------------------------
    st.subheader("Digitized Values")
    for k, v in params.items():
        st.write(f"{k}: {v}")

    # -----------------------------
    # Save to CSV
    # -----------------------------
    df = pd.DataFrame(list(params.items()), columns=["Parameter", "Value"])
    df.to_csv("patient_data.csv", index=False)
    st.success("Data saved to patient_data.csv ✅")
