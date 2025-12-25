# Simple extractor for digitized values
params = {}
words = text.split()
i = 0
while i < len(words):
    if words[i].lower() == "blood" and words[i+1].lower() == "sugar":
        param = "Blood Sugar"
        value = float(words[i+2])
        status = "Normal" if 70 <= value <= 140 else "Abnormal"
        i += 3
    else:
        param = words[i]
        value = float(words[i+1])
        if param.lower() == "hemoglobin":
            status = "Normal" if 12 <= value <= 16 else "Abnormal"
        elif param.lower() == "cholesterol":
            status = "Normal" if value < 200 else "Abnormal"
        else:
            status = "Unknown"
        i += 2
    params[param] = f"{value} --> {status}"

# Display digitized values in Streamlit
st.subheader("Digitized Values")
for k, v in params.items():
    st.write(f"{k}: {v}")
