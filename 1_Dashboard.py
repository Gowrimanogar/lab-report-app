import streamlit as st
import pandas as pd
from extractor import extract_text_from_image

st.title("📋 Lab Report Dashboard")

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    extracted_data = extract_text_from_image(uploaded_file)

    if extracted_data:
        st.session_state["lab_data"] = extracted_data
        df = pd.DataFrame(extracted_data)

        def highlight_status(val):
            if val == "Normal":
                return "background-color: #90EE90"
            else:
                return "background-color: #FF9999"

        st.dataframe(
            df.style.applymap(highlight_status, subset=["Status"]),
            use_container_width=True
        )
    else:
        st.warning("No lab values detected.")
