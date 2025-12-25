import streamlit as st
import pandas as pd
from extractor import extract_text_from_image

st.set_page_config(layout="wide")

st.title("🧪 CBC Lab Report Analysis")

uploaded_file = st.file_uploader(
    "Upload Medical Report (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    with st.spinner("Reading CBC report..."):
        data = extract_text_from_image(uploaded_file)

    if len(data) == 0:
        st.error("❌ Unable to detect CBC values. Please upload a clearer image.")
    else:
        df = pd.DataFrame(data)

        def highlight(val):
            return "color:red;font-weight:bold" if val == "Abnormal" else "color:green;font-weight:bold"

        st.success("✅ CBC tests detected successfully")

        st.dataframe(
            df.style.applymap(highlight, subset=["Status"]),
            use_container_width=True
        )

        # CSV Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "cbc_report.csv",
            "text/csv"
        )
