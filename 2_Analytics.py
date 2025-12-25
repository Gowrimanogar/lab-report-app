import streamlit as st
import pandas as pd

st.title("📊 Report Analytics")

if "lab_data" not in st.session_state:
    st.warning("Upload a lab report first from Dashboard")
else:
    df = pd.DataFrame(st.session_state["lab_data"])
    st.bar_chart(df.set_index("Test")["Value"])
