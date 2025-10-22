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


def create_info_box(params):
    """Crea box informativo con coordinate e parametri"""
    lat = params["lat"]
    lon = params["lon"]
    tilt = params["tilt"]
    azimuth = params["azimuth"]
    albedo = params["albedo"]
    
    return f"""
    <div class="formula-box">
        <div class="formula-title">📍 Coordinate Geografiche</div>
        Latitudine: <b>{lat:.4f}°</b><br>
        Longitudine: <b>{lon:.4f}°</b><br>
        Fuso orario: <b>Europe/Rome</b>
    </div>
    <div class="formula-box">
        <div class="formula-title">🧭 Orientamento Pannelli</div>
        Inclinazione (β): <b>{tilt}°</b><br>
        Azimut: <b>{azimuth}°</b><br>
        Albedo: <b>{albedo:.2f}</b>
    </div>
    """


def display_map_section(params):
    """Visualizza sezione mappa + info"""
    
    location = params.get("location", None)
    if not location:
        return
    
    st.markdown('<p class="section-header">📍 Localizzazione Impianto</p>', unsafe_allow_html=True)
    
    col_map, col_info = st.columns([3, 1], gap="medium")
    screen_width = get_screen_width()
    height_map = CHART_CONFIG["map_height_mobile"] if screen_width <= 480 else CHART_CONFIG["map_height_desktop"]
    
    with col_map:
        m = create_location_map(params["lat"], params["lon"], params["comune"])
        st_folium(m, width="100%", height=height_map)
    
    with col_info:
        st.markdown(create_info_box(params), unsafe_allow_html=True)
