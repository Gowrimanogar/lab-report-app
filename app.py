import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

st.title("Lab Report Digitizer")

uploaded_file = st.file_uploader("Upload Lab Report Image", type=["png","jpg","jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # OCR
    result = reader.readtext(np.array(img))
    text = " ".join([r[1] for r in result])
    st.subheader("OCR Output")
    st.write(text)

    # Here you can continue with your extractor and save to CSV
