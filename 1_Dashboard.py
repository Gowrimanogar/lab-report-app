import streamlit as st
import pandas as pd
from extractor import extract_text_from_image, detect_tests
from fpdf import FPDF

st.title("🧪 Lab Report Dashboard")

uploaded_file = st.file_uploader(
    "Upload Medical Report Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    with st.spinner("🔍 Extracting report data..."):
        text = extract_text_from_image(uploaded_file)
        tests = detect_tests(text)

    if tests:
        df = pd.DataFrame(tests).T

        # Color highlight
        def highlight(row):
            return [
                "background-color: lightgreen" if row["status"] == "Normal"
                else "background-color: lightcoral"
            ] * len(row)

        st.subheader("📊 Test Results")
        st.dataframe(df.style.apply(highlight, axis=1))

        # CSV download
        csv = df.to_csv().encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "lab_report.csv",
            "text/csv"
        )

        # PDF download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Lab Report Summary", ln=True)

        for test, row in df.iterrows():
            pdf.cell(
                200,
                10,
                f"{test}: {row['value']} ({row['status']})",
                ln=True
            )

        st.download_button(
            "⬇ Download PDF",
            pdf.output(dest="S").encode("latin-1"),
            "lab_report.pdf",
            "application/pdf"
        )
    else:
        st.warning("⚠ No lab values detected")
