"""
Modulo per la visualizzazione della mappa interattiva e info impianto
Funzionalità:
- Mappa interattiva con marker località
- Info box parametri impianto
- Layout responsivo
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from config import CHART_CONFIG  # ✅ Import CHART_CONFIG dal config.py


# ==================== UTILITY ====================

def get_screen_width() -> int:
    """
    Rileva larghezza schermo
    
    Returns:
        int: larghezza in pixel (default fallback)
    """
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return CHART_CONFIG.get("screen_width_fallback", 1200)


def get_map_height(screen_width: int) -> int:
    """
    Determina altezza mappa in base alla larghezza schermo
    
    Args:
        screen_width: larghezza schermo in pixel
    
    Returns:
        int: altezza mappa in pixel
    """
    if screen_width <= 480:
        return CHART_CONFIG.get("map_height_mobile", 400)
    else:
        return CHART_CONFIG.get("map_height_desktop", 600)


# ==================== CREAZIONE MAPPA ====================

def create_location_map(lat: float, lon: float, comune: str) -> folium.Map:
    """
    Crea mappa interattiva con marker della località
    
    Args:
        lat: latitudine
        lon: longitudine
        comune: nome del comune
    
    Returns:
        folium.Map
    """
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
    info_items = [
        ("Comune", params.get("comune", "-")),
        ("Latitudine", f"{params['lat']:.4f}°"),
        ("Longitudine", f"{params['lon']:.4f}°"),
        ("Fuso orario", str(params.get('timezone', 'Europe/Rome')).split('/')[-1]),
        ("Numero pannelli / ha", params.get("num_panels", "-")),
        ("Inclinazione (β)", f"{params.get('tilt_pannello', '-')}°"),
        ("Azimut", f"{params.get('azimuth_pannello', '-')}°"),
        ("Albedo", f"{params.get('albedo', 0):.2f}"),
        ("Area pannello", f"{params.get('area', '-')} m²"),
        ("Altezza dal suolo", f"{params.get('altezza', '-')} m"),
        ("Pitch laterale", f"{params.get('pitch_laterale', '-')} m"),
        ("Pitch tra file", f"{params.get('pitch_file', '-')} m"),
        ("Efficienza", f"{params.get('eff', 0)*100 if isinstance(params.get('eff'), float) else params.get('eff')}%"),
        ("Coeff. temperatura", f"{params.get('temp_coeff', 0)*100 if isinstance(params.get('temp_coeff'), float) else params.get('temp_coeff')} %/°C"),
        ("NOCT", f"{params.get('noct', '-')} °C"),
        ("Perdite", f"{params.get('losses', 0)*100 if isinstance(params.get('losses'), float) else params.get('losses')}%"),
    ]
    if params.get("extra_param") and params.get("extra_param") != 0:
        info_items.append(("Parametro extra", params.get("extra_param", "-")))
    return "".join([format_info_item(name, value) for name, value in info_items])


def create_info_box_html(params: dict, height: int) -> str:
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
    """
    Visualizza sezione completa: mappa + info impianto
    """
    if not params.get("location") and not (params.get("lat") and params.get("lon")):
        st.warning("⚠️ Località non disponibile. Inserire coordinate manualmente.")
        return

    st.markdown('<p class="section-header">Resoconto INPUT</p>', unsafe_allow_html=True)

    screen_width = get_screen_width()
    map_height = get_map_height(screen_width)

    col_map, col_info = st.columns([3, 1], gap="medium")

    with col_map:
        location_map = create_location_map(params["lat"], params["lon"], params["comune"])
        st_folium(location_map, width="100%", height=map_height)

    with col_info:
        info_box_html = create_info_box_html(params, map_height)
        st.markdown(info_box_html, unsafe_allow_html=True)
