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

/* Reset e viewport */
* {
    box-sizing: border-box;
}

html {
    font-size: 16px;
}

/* Sfondo globale e font */
:root, body, div[data-testid="stAppViewContainer"], 
div[data-testid="stAppViewContainer"] > .main, div[data-testid="stSidebar"] {
    background-color: white !important;
    font-family: 'Inter', sans-serif;
    color: #000 !important;
}

/* Container principale con max-width per consistenza */
.main .block-container {
    max-width: 1200px;
    padding: 2rem 1rem;
    margin: 0 auto;
}

/* Sidebar */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 280px;
}
[data-testid="stSidebar"] img { 
    max-width: 90%; 
    height: auto; 
    margin-bottom: 1.5rem; 
}

/* Header principale - responsive */
.main-header {
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    padding: 2rem; 
    border-radius: 15px; 
    color: white;
    margin-bottom: 3rem; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}
.main-header h1 { 
    font-size: clamp(1.5rem, 5vw, 2.5rem);
    font-weight: 700; 
    margin-bottom: 0.5rem; 
}
.main-header p { 
    font-size: clamp(0.9rem, 2.5vw, 1.1rem);
    opacity: 0.95; 
    font-weight: 300; 
}

/* Card metriche - responsive */
.metric-card {
    background: white; 
    padding: 1.5rem; 
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
    border-left: 4px solid #74a65b;
    transition: transform 0.2s, box-shadow 0.2s; 
    margin-bottom: 1.5rem;
    min-height: 120px;
}
.metric-card:hover { 
    transform: translateY(-5px); 
    box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
}
.metric-value { 
    font-size: clamp(1.5rem, 4vw, 2.2rem);
    font-weight: 700; 
    color: #74a65b; 
    margin: 0.5rem 0; 
}
.metric-label { 
    font-size: clamp(0.75rem, 2vw, 0.9rem);
    color: #000 !important; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
    font-weight: 600; 
}

/* Sezioni */
.section-header { 
    font-size: clamp(1.2rem, 3vw, 1.6rem);
    font-weight: 600; 
    color: #74a65b; 
    margin: 3rem 0 2rem 0; 
    padding-bottom: 0.5rem; 
    border-bottom: 3px solid #74a65b; 
}

/* Info box */
.formula-box { 
    background: #f8f9fa; 
    border-left: 4px solid #74a65b;
    padding: 1rem; 
    border-radius: 8px; 
    margin: 1.5rem 0; 
    font-family: 'Courier New', monospace; 
    color: #333;
    font-size: clamp(0.8rem, 2vw, 0.95rem);
    overflow-x: auto;
}
.formula-title { 
    font-weight: 600; 
    color: #74a65b;
    margin-bottom: 0.5rem; 
}

/* Pulsanti */
.stButton>button {
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    color: white; 
    border: none; 
    border-radius: 8px;
    padding: 0.5rem 2rem; 
    font-weight: 600; 
    transition: all 0.3s;
    width: 100%;
    max-width: 300px;
}
.stButton>button:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 5px 15px rgba(116,166,91,0.4); 
}

/* Slider nello sidebar */
input[type=range]::-webkit-slider-thumb { background:#74a65b }
input[type=range]::-webkit-slider-runnable-track { background:#a3c68b }
input[type=range]::-moz-range-thumb { background:#74a65b }
input[type=range]::-moz-range-track { background:#a3c68b }
input[type=range]::-ms-thumb { background:#74a65b }
input[type=range]::-ms-track { background:#a3c68b }

/* Grafici */
.stPlotlyChart, .stMatplotlib { 
    background-color: white !important; 
    border-radius: 8px; 
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 100%;
    height: auto;
}

/* Mappa Folium */
.st-folium { 
    background-color: white !important; 
    border-radius: 8px; 
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 100% !important;
    max-width: 100% !important;
}

/* Link */
a, a:visited, a:hover, a:active, .metric-card a {
    color: #74a65b !important;
    text-decoration: none;
}

/* Controlli layer Folium */
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

.leaflet-control-layers label:hover,
.leaflet-control-layers a:hover,
.leaflet-control-layers-toggle:hover {
    background-color: #e6f1df !important;
    color: #74a65b !important;
}

/* === MEDIA QUERIES PER RESPONSIVE === */

/* Tablet (max 1024px) */
@media screen and (max-width: 1024px) {
    .main .block-container {
        max-width: 100%;
        padding: 1.5rem 1rem;
    }
    
    .main-header {
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .section-header {
        margin: 2rem 0 1.5rem 0;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        min-width: 250px;
    }
}

/* Mobile Large (max 768px) */
@media screen and (max-width: 768px) {
    html {
        font-size: 14px;
    }
    
    .main .block-container {
        padding: 1rem 0.75rem;
    }
    
    .main-header {
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 10px;
    }
    
    .metric-card {
        padding: 1rem;
        margin-bottom: 1rem;
        min-height: 100px;
    }
    
    .section-header {
        margin: 1.5rem 0 1rem 0;
    }
    
    .formula-box {
        padding: 0.75rem;
        margin: 1rem 0;
    }
    
    .stButton>button {
        padding: 0.5rem 1.5rem;
        max-width: 100%;
    }
    
    /* Sidebar collassata su mobile */
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 280px !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -280px;
    }
}

/* Mobile Small (max 480px) */
@media screen and (max-width: 480px) {
    html {
        font-size: 13px;
    }
    
    .main .block-container {
        padding: 0.75rem 0.5rem;
    }
    
    .main-header {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        min-height: 90px;
    }
    
    .section-header {
        margin: 1rem 0 0.75rem 0;
    }
    
    .formula-box {
        padding: 0.5rem;
        font-size: 0.75rem;
    }
    
    .stButton>button {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
}

/* Landscape orientation adjustments */
@media screen and (max-height: 600px) and (orientation: landscape) {
    .main-header {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .section-header {
        margin: 1rem 0 0.75rem 0;
    }
    
    .metric-card {
        min-height: 80px;
    }
}

/* Print styles */
@media print {
    .main .block-container {
        max-width: 100%;
    }
    
    .metric-card {
        break-inside: avoid;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
}
</style>
"""

# Applica subito il CSS
st.markdown(CSS, unsafe_allow_html=True)