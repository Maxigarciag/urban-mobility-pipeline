import streamlit as st

st.set_page_config(
    page_title="NYC Citi Bike Analytics",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1 { font-weight: 600; letter-spacing: -0.5px; }
    h4 { font-weight: 400; color: #9aa5b4; margin-bottom: 0.2rem; }
    hr { border-color: #222; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
pg = st.navigation([
    st.Page("pages/1_overview.py", title="Resumen General"),
    st.Page("pages/2_mapa.py", title="Análisis Geográfico"),
    st.Page("pages/3_estaciones.py", title="Flujo de Estaciones"),
])

# --- GLOBAL STYLES & HEADER ---
st.title("NYC Citi Bike Analytics")
st.markdown("<span style='color:#9aa5b4; font-size:0.9rem'>Powered by DuckDB · Streamlit · PyDeck · Plotly</span>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Run the selected page
pg.run()
