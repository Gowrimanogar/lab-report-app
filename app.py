import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Lab Report Digitizer",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# GLOBAL STYLING (FIX 3 – BEAUTIFUL PROFESSIONAL UI)
# -------------------------------------------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid #1e293b;
}

/* CARDS */
.card {
    background: rgba(15, 23, 42, 0.85);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #1e293b;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

/* HEADINGS */
h1 {
    color: #38bdf8;
    font-size: 48px;
    font-weight: 800;
}

h2 {
    color: #7dd3fc;
}

h3 {
    color: #bae6fd;
}

/* TEXT */
p {
    color: #e5e7eb;
    font-size: 18px;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(90deg, #38bdf8, #0ea5e9);
    color: black;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0ea5e9, #38bdf8);
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background-color: #020617;
    border-radius: 15px;
    padding: 15px;
    border: 1px dashed #38bdf8;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #94a3b8;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown("""
<div class="card">
    <h1>🧪 AI Lab Report Digitizer</h1>
    <p>
        Upload medical lab reports and instantly convert them into 
        <b>digital analytics, abnormal highlights, and downloadable reports</b>.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# FEATURES SECTION
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📷 Image to Data</h3>
        <p>Upload scanned lab reports or photos and extract test values automatically.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>🟢🔴 Abnormal Detection</h3>
        <p>Normal values appear in green and abnormal results highlighted in red.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>📄 Download Reports</h3>
        <p>Export analyzed reports in <b>PDF</b> and <b>CSV</b> formats.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# HOW TO USE
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h2>🚀 How to Use</h2>
    <ol style="color:#e5e7eb; font-size:18px;">
        <li>Go to the <b>Dashboard</b> from the sidebar</li>
        <li>Upload your medical lab report image</li>
        <li>View extracted test values and abnormal highlights</li>
        <li>Download PDF or CSV reports</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# MEDICAL IMAGE (RELATED & SAFE)
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.image(
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
    caption="AI-powered medical diagnostics",
    use_container_width=True
)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("""
<div class="footer">
    © 2025 AI Lab Report Digitizer • Built with Streamlit & OCR
</div>
""", unsafe_allow_html=True)
