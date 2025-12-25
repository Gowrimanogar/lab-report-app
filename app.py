import streamlit as st

st.set_page_config(
    page_title="Lab Report Digitizer",
    page_icon="🧪",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-image: url("https://images.unsplash.com/photo-1559757175-5700dde675bc");
    background-size: cover;
}
.main {
    background: rgba(0,0,0,0.80);
    padding: 40px;
    border-radius: 20px;
}
h1, h2, p {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main">
<h1>🧪 AI Lab Report Digitizer</h1>
<p>Upload medical reports → get digital analytics instantly</p>
<hr>
<h3>⬅ Use the sidebar to navigate</h3>
</div>
""", unsafe_allow_html=True)
