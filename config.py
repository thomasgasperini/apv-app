CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

* { box-sizing: border-box; }
html { font-size: 16px; overflow-x: hidden; }

/* Sfondo e font */
:root, body, div[data-testid="stAppViewContainer"], 
div[data-testid="stAppViewContainer"] > .main, div[data-testid="stSidebar"] {
    background-color: white !important;
    font-family: 'Inter', sans-serif;
    color: #000 !important;
}

/* Container principale */
.main .block-container {
    width: 100%;
    max-width: min(1500px, 100vw);
    padding: clamp(1rem, 2vw, 2rem) clamp(0.75rem, 2vw, 1rem);
    margin: 0 auto;
    transition: all 0.2s ease-in-out;
}

/* Sidebar */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 300px !important;
    max-width: 380px !important;
}
[data-testid="stSidebar"] {
    min-width: 300px !important;
    max-width: 420px !important;
    width: 380px !important;
    transition: width 0.3s ease-in-out;
}

/* Sidebar mobile */
@media screen and (max-width: 768px) {
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 300px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -300px;
        transition: margin-left 0.3s ease-in-out;
    }
}

/* Header principale */
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

/* Card metriche */
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border-left: 4px solid #74a65b;
    transition: transform 0.2s, box-shadow 0.2s;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    word-break: normal;
    text-align: center;
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

/* Consenti multilinea per mobile */
@media screen and (max-width: 480px) {
    .metric-label {
        white-space: normal;
    }
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Titoli di sezione */
.section-header {
    font-size: clamp(1.2rem, 3vw, 1.6rem);
    font-weight: 600;
    color: #74a65b;
    margin: 3rem 0 2rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #74a65b;
}

/* Formula box */
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

/* === GRID RESPONSIVA PER LE METRICHE === */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    width: 100%;
    margin-top: 1rem;
}

/* Adattamento per schermi molto piccoli */
@media screen and (max-width: 480px) {
    .metrics-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}

/* Grafici e mappe */
.stPlotlyChart, .stMatplotlib, .st-folium {
    background-color: white !important;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 100%;
    height: auto;
}

/* Link */
a, a:visited, a:hover, a:active, .metric-card a {
    color: #74a65b !important;
    text-decoration: none;
}
</style>
"""
