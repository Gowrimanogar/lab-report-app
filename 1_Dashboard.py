import streamlit as st
import pandas as pd
from extractor import extract_text_from_image

st.title("📊 CBC Lab Report Analysis")

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    with st.spinner("Analyzing report..."):
        data = extract_text_from_image(uploaded_file)

    if not data:
        st.warning("⚠ No lab tests detected.")
    else:
        df = pd.DataFrame(data)

        def color_status(val):
            if val == "Abnormal":
                return "color: red; font-weight: bold"
            return "color: green; font-weight: bold"

        st.subheader("🧪 Extracted CBC Values")
        st.dataframe(df.style.applymap(color_status, subset=["Status"]))

        # CSV Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "cbc_report.csv",
            "text/csv"
        )

        # PDF Download (Simple)
        st.info("📄 PDF download will be enabled in next step")
