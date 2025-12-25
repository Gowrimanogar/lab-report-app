import streamlit as st

st.title("📊 Report Analytics")

if "df" not in st.session_state:
    st.warning("Upload a lab report first from Dashboard")
else:
    df = st.session_state["df"]
    st.bar_chart(df.set_index("Test")["Value"])
