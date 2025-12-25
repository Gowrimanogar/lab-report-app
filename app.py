import streamlit as st
from PIL import Image
import pytesseract
from PIL import ImageEnhance, ImageFilter
from extractor import extract_parameters, classify
from data_store import save_data

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("Lab Report Digitizer")

uploaded_file = st.file_uploader("Upload Lab Report Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    # OCR
    img_gray = img.convert('L')
    img_gray = ImageEnhance.Contrast(img_gray).enhance(3)
    img_gray = img_gray.filter(ImageFilter.SHARPEN)
    
    text = pytesseract.image_to_string(img_gray)
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    
    st.subheader("OCR Output")
    st.write(text)
    
    # Extract parameters
    params = extract_parameters(text)
    
    final_data = {}
    st.subheader("Digitized Values")
    for p, v in params.items():
        status = classify(p, v)
        final_data[p] = {"value": v, "status": status}
        st.write(f"{p}: {v} --> {status}")
        easyocr

    
    # Save data
    save_data(final_data)
    st.success("Data saved to patient_data.csv ✅")

