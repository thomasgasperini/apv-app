"""
Configurazione centralizzata per PV Simulator
Contiene: costanti, parametri default, stili CSS, configurazioni UI
"""

from zoneinfo import ZoneInfo

# ==================== COSTANTI FISICHE ====================
HECTARE_M2 = 10000  # 1 ettaro in m²
TIMEZONE = "Europe/Rome"
TIMEZONE_OBJ = ZoneInfo(TIMEZONE)

# ==================== PARAMETRI DEFAULT ====================
DEFAULT_PARAMS = {
    # Localizzazione
    "comune": "Roma",
    "lat": 41.9,
    "lon": 12.5,
    
    # Pannello
    "num_panels": 1,
    "base": 1.0,  # m
    "altezza_pannello": 1.0,  # m
    
    # Geometria installazione
    "altezza": 1.0,  # m dal suolo
    "pitch_laterale": 1.0,  # m
    "pitch_file": 2.0,  # m
    "tilt": 30,  # gradi
    "azimuth": 0, 
    
    # Caratteristiche elettriche
    "eff": 0.20,  # efficienza 20%
    "noct": 45.0,  # °C
    "temp_coeff": -0.004,  # %/°C
    "losses": 0.10,  # perdite di sistema 10%
    "albedo": 0.2,  # riflettanza del suolo
}

# ==================== COLORI TEMA ====================
COLORS = {
    "primary": "#74a65b",
    "secondary": "#a3c68b",
    "accent": "#f7e08e",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "white": "#ffffff",
    "text": "#000000",
    "light_bg": "#f8f9fa",
}

# ==================== CONFIGURAZIONE GRAFICI ====================
CHART_CONFIG = {
    "fig_height": 4,
    "fig_width_min": 10,
    "fig_width_max": 14,
    "screen_width_fallback": 1200,
    "map_height_mobile": 300,
    "map_height_desktop": 400,
}

# ==================== MESSAGGI UI ====================
MESSAGES = {
    "location_not_found": "⚠️ Comune non trovato",
    "location_success": "{lat:.4f}°N, {lon:.4f}°E",
    "surface_warning": "⚠️ La superficie totale ({superficie:.0f} m²) supera 1 ettaro.",
    "surface_exceed": "⚠️ La disposizione dei pannelli supera 1 ettaro! Superficie: {superficie:.0f} m²",
    "surface_valid": "✅ Input validi: {superficie:.0f} m² ({gcr:.2%} GCR)",
}

# ==================== CONFIGURAZIONE PAGINA ====================
PAGE_CONFIG = {
    "page_title": "Analisi Produzione Fotovoltaico",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ==================== ASSETS ====================
LOGO_URL = "http://www.resfarm.it/wp-content/uploads/2025/02/Logo_Resfarm_home_white.svg#121"

# ==================== CSS GLOBALE ====================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* ===== RESET BASE ===== */
* { box-sizing: border-box; }
html { font-size: 16px; overflow-x: hidden; }
body, :root, div[data-testid="stAppViewContainer"], 
div[data-testid="stAppViewContainer"] > .main, 
div[data-testid="stSidebar"] {
    background-color: white !important;
    font-family: 'Inter', sans-serif;
    color: #000 !important;
}

/* ===== LAYOUT PRINCIPALE ===== */
.main, section.main, [data-testid="stAppViewContainer"] .main,
section.main > div, section.main > div > div,
.main .block-container, .appview-container .main .block-container {
    width: 100% !important;
    max-width: none !important;
    padding: 1rem !important;
    margin: 0 !important;
    transition: none !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] > div:first-child {
    display: flex !important;
    flex-direction: column;
    align-items: stretch !important;
    padding-top: 1rem !important;
    min-width: 200px !important;
    max-width: 380px !important;
}

[data-testid="stSidebar"][aria-expanded="true"] { 
    width: 380px !important; 
    transition: width 0.3s ease-in-out; 
}
[data-testid="stSidebar"][aria-expanded="false"] { 
    width: 200px !important; 
    transition: width 0.3s ease-in-out; 
}

@media screen and (max-width: 768px) {
    [data-testid="stSidebar"][aria-expanded="true"] { width: 300px !important; }
    [data-testid="stSidebar"][aria-expanded="false"] { 
        margin-left: -300px; 
        transition: margin-left 0.3s ease-in-out; 
    }
}

[data-testid="stSidebar"] > div:first-child > * {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* ===== HEADER PRINCIPALE ===== */
.main-header {
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    padding: clamp(1rem, 5vw, 2rem);
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

/* ===== GRID E COLONNE ===== */
[data-testid="stHorizontalBlock"] {
    display: flex !important; 
    gap: 1.5rem !important; 
    width: 100% !important; 
    flex-wrap: wrap !important;
}
[data-testid="stHorizontalBlock"] > div,
[data-testid="column"] { 
    flex: 1 1 calc(33.333% - 1rem) !important; 
    min-width: 250px !important; 
    max-width: 100% !important; 
}

.metrics-grid {
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem; 
    width: 100% !important; 
    margin-top: 1rem;
}

/* ===== CARD METRICHE ===== */
.metric-card {
    background: white; 
    padding: 1rem; 
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
    border-left: 4px solid #74a65b;
    transition: transform 0.2s, box-shadow 0.2s;
    min-height: 120px; 
    width: 100% !important;
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    text-align: center;
}
.metric-card:hover { 
    transform: translateY(-5px); 
    box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
}
.metric-value { 
    font-size: clamp(1.5rem, 2.5vw, 2rem); 
    font-weight: 700; 
    color: #74a65b; 
    margin: 0.25rem 0; 
    line-height: 1.2; 
}
.metric-label { 
    font-size: clamp(0.75rem, 1.8vw, 0.85rem); 
    color: #000 !important; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
    font-weight: 600; 
    white-space: nowrap; 
}

/* ===== TITOLI SEZIONE ===== */
.section-header {
    font-size: clamp(1.2rem, 3vw, 1.6rem); 
    font-weight: 600; 
    color: #74a65b;
    margin: 3rem 0 2rem 0; 
    padding-bottom: 0.5rem; 
    border-bottom: 3px solid #74a65b;
}

/* ===== FORMULA BOX ===== */
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

/* ===== PULSANTI ===== */
.stButton>button {
    width: 100% !important; 
    max-width: 300px !important; 
    min-width: 200px !important;
    margin-bottom: 1rem; 
    border-radius: 8px;
    background: linear-gradient(135deg, #74a65b 0%, #a3c68b 100%);
    color: white; 
    border: none; 
    padding: 0.5rem 1.5rem; 
    font-weight: 600;
    transition: all 0.3s;
}
.stButton>button:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 5px 15px rgba(116,166,91,0.4); 
}

[data-testid="stSidebar"][aria-expanded="false"] > div:first-child .stButton>button {
    max-width: 100% !important; 
    min-width: 0 !important;
}

/* ===== GRAFICI E MAPPE ===== */
.stPlotlyChart, .stMatplotlib, .st-folium {
    background-color: white !important; 
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    width: 100%; 
    height: auto;
}

/* ===== LINK ===== */
a, a:visited, a:hover, a:active, .metric-card a { 
    color: #74a65b !important; 
    text-decoration: none; 
}

/* ===== SCROLLBAR PERSONALIZZATA ===== */
.formula-box::-webkit-scrollbar {
    width: 8px;
}
.formula-box::-webkit-scrollbar-track {
    background: #ffffff;
    border-radius: 4px;
}
.formula-box::-webkit-scrollbar-thumb {
    background-color: #74a65b;
    border-radius: 4px;
    border: 2px solid #ffffff;
}
.formula-box {
    scrollbar-width: thin;
    scrollbar-color: #74a65b #ffffff;
}

/* ===== INFO ITEM ===== */
.info-item {
    background: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* ===== RESPONSIVE ===== */
@media screen and (max-width: 768px) {
    [data-testid="stHorizontalBlock"] > div,
    [data-testid="column"] { flex: 1 1 100% !important; }
    .metrics-grid { grid-template-columns: 1fr; gap: 1rem; }
    .metric-label { white-space: normal; }
}

@media screen and (max-width: 480px) {
    .metrics-grid { grid-template-columns: 1fr; gap: 1rem; }
    .metric-label { white-space: normal; }
}
</style>
"""