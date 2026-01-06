import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
from pyzbar.pyzbar import decode
import io

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Lab Report Generator", layout="centered")

st.title("🧪 Lab Report Generator App")
st.write("Upload a Medical Report image OR a QR / Barcode image")

# ------------------ FUNCTIONS ------------------

def scan_qr_or_barcode(image):
    decoded_objects = decode(image)
    results = []
    for obj in decoded_objects:
        results.append(obj.data.decode("utf-8"))
    return results


def extract_text_from_image(image):
    return pytesseract.image_to_string(image)


def extract_tests(text):
    lines = text.split("\n")
    data = []

    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            try:
                test_name = " ".join(parts[:-1])
                value = float(parts[-1])
                data.append([test_name, value])
            except:
                pass

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data, columns=["Test Name", "Value"])


# ------------------ FILE UPLOAD ------------------

uploaded_file = st.file_uploader(
    "📤 Upload Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # -------- QR / BARCODE CHECK --------
    qr_results = scan_qr_or_barcode(image)

    if qr_results:
        st.success("✅ QR / Barcode Detected")
        for result in qr_results:
            st.write("🔗 Data:", result)

    else:
        # -------- MEDICAL REPORT OCR --------
        st.info("🔍 No QR found. Processing as Medical Report...")

        extracted_text = extract_text_from_image(image)

        if extracted_text.strip() == "":
            st.error("❌ No text detected. Try a clearer image.")
        else:
            df = extract_tests(extracted_text)

            if df.empty:
                st.warning("⚠ No test values detected.")
                st.text_area("Extracted Text", extracted_text, height=200)
            else:
                st.success("✅ Test Results Detected")
                st.dataframe(df)

                # -------- CSV DOWNLOAD --------
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="lab_report.csv",
                    mime="text/csv"
                )

else:
    st.info("👆 Please upload an image to begin.")
