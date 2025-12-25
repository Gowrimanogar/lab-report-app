uploaded_file = st.file_uploader("Upload Medical Report", type=["png","jpg","jpeg"])

if uploaded_file:
    data = extract_text_from_image(uploaded_file)

    if data:
        st.session_state["lab_data"] = data
        df = pd.DataFrame(data)

        def color_status(val):
            return "background-color: #7CFC98" if val == "Normal" else "background-color: #FF7F7F"

        st.dataframe(df.style.applymap(color_status, subset=["Status"]))
