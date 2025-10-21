import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="PV Energy Calculator Pro",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* Sfondo globale e font */
:root, body, div[data-testid="stAppViewContainer"], 
div[data-testid="stAppViewContainer"] > .main, div[data-testid="stSidebar"] {
    background-color: white !important;
    font-family: 'Inter', sans-serif;
    color: #000 !important;
}

/* Sidebar */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
}
[data-testid="stSidebar"] img { max-width: 90%; height: auto; margin-bottom: 1.5rem; }

/* Header principale */
.main-header {
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    padding: 2rem; border-radius: 15px; color: white;
    margin-bottom: 3rem; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}
.main-header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.main-header p { font-size: 1.1rem; opacity: 0.95; font-weight: 300; }

/* Card metriche */
.metric-card {
    background: white; padding: 1.5rem; border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 4px solid #74a65b;
    transition: transform 0.2s, box-shadow 0.2s; margin-bottom: 1.5rem;
}
.metric-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
.metric-value { font-size: 2.2rem; font-weight: 700; color: #74a65b; margin: 0.5rem 0; }
.metric-label { font-size: 0.9rem; color: #000 !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }

/* Sezioni */
.section-header { font-size: 1.6rem; font-weight: 600; color: #74a65b; margin: 3rem 0 2rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #74a65b; }

/* Info box */
/* Info box */
.formula-box { 
    background: #f8f9fa; 
    border-left: 4px solid #74a65b;  /* cambiamo il colore del bordo */
    padding: 1rem; 
    border-radius: 8px; 
    margin: 1.5rem 0; 
    font-family: 'Courier New', monospace; 
    color: #333;  /* testo scuro neutro */
}
.formula-title { 
    font-weight: 600; 
    color: #74a65b;  /* titolo verde */
    margin-bottom: 0.5rem; 
}

/* Pulsanti */
.stButton>button {
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    color: white; border: none; border-radius: 8px;
    padding: 0.5rem 2rem; font-weight: 600; transition: all 0.3s;
}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(116,166,91,0.4); }

/* Slider nello sidebar */
input[type=range]::-webkit-slider-thumb { background:#74a65b }
input[type=range]::-webkit-slider-runnable-track { background:#a3c68b }
input[type=range]::-moz-range-thumb { background:#74a65b }
input[type=range]::-moz-range-track { background:#a3c68b }
input[type=range]::-ms-thumb { background:#74a65b }
input[type=range]::-ms-track { background:#a3c68b }

/* Grafici */
.stPlotlyChart, .stMatplotlib { background-color: white !important; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

/* Mappa Folium */
.st-folium { background-color: white !important; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

/* Tutti i link e linguette Markdown */
a, a:visited, a:hover, a:active, .metric-card a {
    color: #74a65b !important;
    text-decoration: none;
}

/* Linguette / controlli layer Folium */
.leaflet-control-layers, 
.leaflet-control-layers a,
.leaflet-control-layers label,
.leaflet-control-layers-toggle {
    background-color: #f8f9fa !important;
    color: #74a65b !important;
    border: 1px solid #74a65b !important;
    border-radius: 5px !important;
    font-weight: 600 !important;
}

/* Hover sui layer */
.leaflet-control-layers label:hover,
.leaflet-control-layers a:hover,
.leaflet-control-layers-toggle:hover {
    background-color: #e6f1df !important;
    color: #74a65b !important;
}
</style>
"""

# Applica subito il CSS
st.markdown(CSS, unsafe_allow_html=True)
