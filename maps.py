# maps.py
"""
Modulo per la visualizzazione della mappa interattiva
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from config import CHART_CONFIG


def get_screen_width():
    """Rileva larghezza schermo"""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return CHART_CONFIG["screen_width_fallback"]


def create_location_map(lat, lon, comune):
    """Crea mappa interattiva con marker"""
    m = folium.Map(location=[lat, lon], zoom_start=6, tiles='Cartodb Positron')
    folium.Marker(
        [lat, lon],
        tooltip=comune,
        popup=f"<b>{comune}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
        icon=folium.Icon(color='green', icon='sun', prefix='fa')
    ).add_to(m)
    return m


def create_info_box_content(params):
    """Contenuto interno dell'info box in colonne dinamiche"""
    info_items = [
        ("Comune", params.get("comune", "-")),
        ("Latitudine", f"{params['lat']:.4f}°"),
        ("Longitudine", f"{params['lon']:.4f}°"),
        ("Fuso orario", params.get('timezone', 'Europe/Rome')),
        ("Numero pannelli / ha", params.get("num_panels", "-")),
        ("Inclinazione (β)", f"{params.get('tilt', '-')}°"),
        ("Azimut", f"{params.get('azimuth', '-')}°"),
        ("Albedo", f"{params.get('albedo', '-'):.2f}"),
        ("Area pannello", f"{params.get('area', '-')} m²"),
        ("Altezza dal suolo", f"{params.get('altezza', '-')} m"),
        ("Pitch laterale", f"{params.get('pitch_laterale', '-')} m"),
        ("Pitch tra file", f"{params.get('pitch_file', '-')} m"),
        ("Efficienza", f"{params.get('eff', '-')*100 if isinstance(params.get('eff'), float) else params.get('eff')}%"),
        ("Temp coeff.", f"{params.get('temp_coeff', '-')*100 if isinstance(params.get('temp_coeff'), float) else params.get('temp_coeff')} %/°C"),
        ("NOCT", f"{params.get('noct', '-') } °C"),
        ("Perdite", f"{params.get('losses', '-')*100 if isinstance(params.get('losses'), float) else params.get('losses')}%"),
        ("Extra param", params.get("extra_param", "-"))
    ]

    return "".join([f'<div class="info-item"><b>{name}:</b> {value}</div>' for name, value in info_items])


def display_map_section(params):
    """Visualizza sezione mappa + info con altezza allineata e font monospace"""
    location = params.get("location", None)
    if not location:
        return

    st.markdown('<p class="section-header">📍 Descrizione Impianto</p>', unsafe_allow_html=True)

    col_map, col_info = st.columns([3, 1], gap="medium")
    screen_width = get_screen_width()
    height_map = CHART_CONFIG["map_height_mobile"] if screen_width <= 480 else CHART_CONFIG["map_height_desktop"]

    with col_map:
        m = create_location_map(params["lat"], params["lon"], params["comune"])
        st_folium(m, width="100%", height=height_map)

    with col_info:
        st.markdown(f"""
        <div class="formula-box" style="
            height: {height_map}px;
            overflow-y: auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.25rem 0.5rem;
            padding: 0.5rem 0.25rem;
            margin: 0;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
        ">
            {create_info_box_content(params)}
        </div>
        <style>
            .info-item {{
                background: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }}
            /* Scrollbar personalizzata */
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
            /* Firefox */
            .formula-box {{
                scrollbar-width: thin;
                scrollbar-color: #74a65b #ffffff;
            }}
        </style>
        """, unsafe_allow_html=True)
