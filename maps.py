"""
Modulo per la visualizzazione della mappa interattiva e info impianto
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from config import CHART_CONFIG


# ==================== UTILITY ====================

def get_screen_width() -> int:
    """Rileva larghezza schermo"""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return CHART_CONFIG.get("screen_width_fallback", 1200)


def get_map_height(screen_width: int) -> int:
    """Determina altezza mappa in base alla larghezza schermo"""
    if screen_width <= 480:
        return CHART_CONFIG.get("map_height_mobile", 400)
    else:
        return CHART_CONFIG.get("map_height_desktop", 600)


# ==================== CREAZIONE MAPPA ====================

def create_location_map(lat: float, lon: float, comune: str) -> folium.Map:
    """Crea mappa interattiva con marker della località"""
    m = folium.Map(
        location=[lat, lon], 
        zoom_start=6, 
        tiles='Cartodb Positron'
    )
    folium.Marker(
        [lat, lon],
        tooltip=comune,
        popup=f"<b>{comune}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
        icon=folium.Icon(color='green', icon='sun', prefix='fa')
    ).add_to(m)
    return m


# ==================== INFO BOX ====================

def format_info_item(name: str, value) -> str:
    return f'<div class="info-item"><b>{name}:</b> {value}</div>'


def create_info_box_content(params: dict) -> str:
    """Crea contenuto info box con parametri input"""
    info_items = [
        ("Comune", params.get("comune", "-")),
        ("Latitudine", f"{params['lat']:.3f}°"),
        ("Longitudine", f"{params['lon']:.3f}°"),
        ("Fuso orario", str(params.get('timezone', 'Europe/Rome')).split('/')[-1]),
        ("N. pannelli totali", params.get("num_panels_total", "-")),
        ("Layout", f"{params.get('num_panels_per_row', '-')} pannelli × {params.get('num_rows', '-')} file"),
        ("Dimensione pannello",  f"{params.get('lato_minore', '-')} × {params.get('lato_maggiore', '-')} m"),
        ("Area pannello", f"{params.get('area_pannello', '-'):.2f} m²"),
        ("Inclinazione (β)", f"{params.get('tilt_pannello', '-')}°"),
        ("Azimut", f"{params.get('azimuth_pannello', '-')}°"),
        ("Distanza tra file", f"{params.get('distanza_interfile', '-')} m"),
        ("Pitch laterale", f"{params.get('pitch_laterale', '-')} m"),
        ("Efficienza", f"{params.get('eff', 0)*100 if isinstance(params.get('eff'), float) else params.get('eff')}%"),
        ("Coeff. temperatura", f"{params.get('temp_coeff', 0)*100 if isinstance(params.get('temp_coeff'), float) else params.get('temp_coeff')} %/°C"),
        ("NOCT", f"{params.get('noct', '-')} °C"),
        ("Perdite sistema", f"{params.get('losses', 0)*100 if isinstance(params.get('losses'), float) else params.get('losses')}%"),
        ("Albedo", f"{params.get('albedo', 0):.2f}"),
        ("Ettari campo", f"{params.get('hectares', '-')}"),
    ]
    
    return "".join([format_info_item(name, value) for name, value in info_items])


def create_info_box_html(params: dict, height: int) -> str:
    """Crea HTML info box con stile"""
    content = create_info_box_content(params)
    return f"""
    <div class="formula-box" style="
        height: {height}px;
        overflow-y: auto;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.25rem 0.5rem;
        padding: 0.5rem 0.25rem;
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    ">
        {content}
    </div>
    <style>
        .info-item {{
            background: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .formula-box::-webkit-scrollbar {{
            width: 8px;
        }}
        .formula-box::-webkit-scrollbar-track {{
            background: #ffffff;
            border-radius: 4px;
        }}
        .formula-box::-webkit-scrollbar-thumb {{
            background-color: #74a65b;
            border-radius: 4px;
            border: 2px solid #ffffff;
        }}
        .formula-box {{
            scrollbar-width: thin;
            scrollbar-color: #74a65b #ffffff;
        }}
    </style>
    """


# ==================== FUNZIONE PRINCIPALE ====================

def display_map_section(params: dict):
    """Visualizza sezione completa: mappa + info impianto"""
    if not params.get("location") and not (params.get("lat") and params.get("lon")):
        st.warning("Località non disponibile. Inserire coordinate manualmente.")
        return

    st.markdown('<p class="section-header">Resoconto dati di INPUT</p>', unsafe_allow_html=True)

    screen_width = get_screen_width()
    map_height = get_map_height(screen_width)

    col_info, col_map = st.columns([2, 1], gap="medium")

    with col_info:
        info_box_html = create_info_box_html(params, map_height)
        st.markdown(info_box_html, unsafe_allow_html=True)

    with col_map:
        location_map = create_location_map(params["lat"], params["lon"], params["comune"])
        st_folium(location_map, width="100%", height=map_height)
