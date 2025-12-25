import streamlit as st
import pandas as pd
from extractor import extract_text_from_image
from io import BytesIO
from fpdf import FPDF

st.title("📊 CBC Lab Report Analysis")

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    data = extract_text_from_image(uploaded_file)

    if data:
        df = pd.DataFrame(data)

        def color_status(val):
            return "color: green" if val == "Normal" else "color: red"

        st.dataframe(df.style.applymap(color_status, subset=["Status"]))

        # CSV DOWNLOAD
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "lab_report.csv",
            "text/csv"
        )

        # PDF DOWNLOAD
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        for row in df.itertuples():
            pdf.cell(0, 8, f"{row.Test}: {row.Value} ({row.Status})", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "⬇ Download PDF",
            pdf_bytes,
            "lab_report.pdf",
            "application/pdf"
        )

    else:
        st.warning("No lab tests detected.")
