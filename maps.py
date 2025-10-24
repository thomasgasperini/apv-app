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
from config import CHART_CONFIG


# ==================== UTILITY ====================

def get_screen_width() -> int:
    """
    Rileva larghezza schermo
    
    Returns:
        int: larghezza in pixel (default 1200)
    """
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return CHART_CONFIG["screen_width_fallback"]


def get_map_height(screen_width: int) -> int:
    """
    Determina altezza mappa in base alla larghezza schermo
    
    Args:
        screen_width: larghezza schermo in pixel
    
    Returns:
        int: altezza mappa in pixel
    """
    if screen_width <= 480:
        return CHART_CONFIG["map_height_mobile"]
    else:
        return CHART_CONFIG["map_height_desktop"]


# ==================== CREAZIONE MAPPA ====================

def create_location_map(lat: float, lon: float, comune: str) -> folium.Map:
    """
    Crea mappa interattiva con marker della località
    
    Args:
        lat: latitudine
        lon: longitudine
        comune: nome del comune
    
    Returns:
        oggetto folium.Map
    """
    # Crea mappa centrata sulla località
    m = folium.Map(
        location=[lat, lon], 
        zoom_start=6, 
        tiles='Cartodb Positron'
    )
    
    # Aggiungi marker
    folium.Marker(
        [lat, lon],
        tooltip=comune,
        popup=f"<b>{comune}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
        icon=folium.Icon(color='green', icon='sun', prefix='fa')
    ).add_to(m)
    
    return m


# ==================== INFO BOX ====================

def format_info_item(name: str, value) -> str:
    """
    Formatta singolo elemento informativo
    
    Args:
        name: nome parametro
        value: valore parametro
    
    Returns:
        HTML string
    """
    return f'<div class="info-item"><b>{name}:</b> {value}</div>'


def create_info_box_content(params: dict) -> str:
    """
    Crea contenuto HTML per info box con tutti i parametri
    
    Args:
        params: dizionario parametri impianto
    
    Returns:
        HTML string
    """
    # Lista parametri da visualizzare
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
        (
            "Efficienza", 
            f"{params.get('eff', 0)*100 if isinstance(params.get('eff'), float) else params.get('eff')}%"
        ),
        (
            "Coeff. temperatura", 
            f"{params.get('temp_coeff', 0)*100 if isinstance(params.get('temp_coeff'), float) else params.get('temp_coeff')} %/°C"
        ),
        ("NOCT", f"{params.get('noct', '-')} °C"),
        (
            "Perdite", 
            f"{params.get('losses', 0)*100 if isinstance(params.get('losses'), float) else params.get('losses')}%"
        ),
    ]
    
    # Aggiungi extra param se presente
    if params.get("extra_param") and params.get("extra_param") != 0:
        info_items.append(("Parametro extra", params.get("extra_param", "-")))
    
    # Genera HTML
    return "".join([format_info_item(name, value) for name, value in info_items])


def create_info_box_html(params: dict, height: int) -> str:
    """
    Crea HTML completo per info box con styling
    
    Args:
        params: parametri impianto
        height: altezza box in pixel
    
    Returns:
        HTML string completo con stili
    """
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
        
        /* Scrollbar personalizzata - Webkit (Chrome, Safari, Edge) */
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
        
        /* Scrollbar personalizzata - Firefox */
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
    
    Args:
        params: dizionario con tutti i parametri
    """
    # Verifica presenza location
    if not params.get("location") and not (params.get("lat") and params.get("lon")):
        st.warning("⚠️ Località non disponibile. Inserire coordinate manualmente.")
        return
    
    # Header sezione
    st.markdown(
        '<p class="section-header">Resoconto INPUT</p>', 
        unsafe_allow_html=True
    )
    
    # Determina altezza in base allo schermo
    screen_width = get_screen_width()
    map_height = get_map_height(screen_width)
    
    # Layout a 2 colonne: mappa (70%) + info (30%)
    col_map, col_info = st.columns([3, 1], gap="medium")
    
    # COLONNA MAPPA
    with col_map:
        location_map = create_location_map(
            params["lat"], 
            params["lon"], 
            params["comune"]
        )
        st_folium(location_map, width="100%", height=map_height)
    
    # COLONNA INFO
    with col_info:
        info_box_html = create_info_box_html(params, map_height)
        st.markdown(info_box_html, unsafe_allow_html=True)