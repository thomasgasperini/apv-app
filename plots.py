import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import pandas as pd
from config import CSS  # Importa il CSS globale

# Applica il CSS (già fatto in config.py, ma sicuro)
st.markdown(CSS, unsafe_allow_html=True)

def plot_graphs(params, results):
    times = results["times"]
    P_ac = results["P_ac"]
    poa = results["poa"]
    clearsky = results["clearsky"]
    comune = params["comune"]
    data = params["data"]
    lat = params["lat"]
    lon = params["lon"]
    location = params.get("location", None)

    # -----------------------
    # ⚡ Risultati principali (card HTML/CSS)
    # -----------------------
    st.markdown('<p class="section-header">⚡ Risultati di Produzione</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Energia Giornaliera</div>
        <div class="metric-value">{results['E_day']:.2f} kWh</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Picco di Potenza</div>
        <div class="metric-value">{P_ac.max():.0f} W</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Irradianza Max</div>
        <div class="metric-value">{poa['poa_global'].max():.0f} W/m²</div>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Energia Annuale Est.</div>
        <div class="metric-value">{results['E_day']*365:.0f} kWh</div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------
    # 🗺️ Mappa Interattiva
    # -----------------------
    if location:
        st.markdown('<p class="section-header">📍 Localizzazione Impianto</p>', unsafe_allow_html=True)
        col_map, col_info = st.columns([2, 1])

        with col_map:
            m = folium.Map(location=[lat, lon], zoom_start=6, tiles='Cartodb Positron')
            folium.Marker(
                [lat, lon],
                tooltip=comune,
                popup=f"<b>{comune}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
                icon=folium.Icon(color='green', icon='sun', prefix='fa')
            ).add_to(m)
            st_folium(m, width="100%", height=400)

        with col_info:
            st.markdown(f"""
            <div class="formula-box">
                <div class="formula-title">📐 Coordinate Geografiche</div>
                Latitudine: <b>{lat:.4f}°</b><br>
                Longitudine: <b>{lon:.4f}°</b><br>
                Fuso orario: <b>Europe/Rome</b>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="formula-box">
                <div class="formula-title">🧭 Orientamento</div>
                Inclinazione (β): <b>{params['tilt']}°</b><br>
                Azimut: <b>{params['azimuth']}°</b><br>
                Albedo: <b>{params['albedo']:.2f}</b>
            </div>
            """, unsafe_allow_html=True)


    # -----------------------
    # 📈 Grafici affiancati: Produzione & Irradianza
    # -----------------------
    st.markdown('<p class="section-header">📈 Analisi Dettagliata</p>', unsafe_allow_html=True)
    col_prod, col_irr = st.columns(2)

    # Grafico Produzione
    with col_prod:
        fig, ax = plt.subplots(figsize=(6,4))
        ax.fill_between(times, P_ac, alpha=0.3, color='#74a65b')
        ax.plot(times, P_ac, linewidth=2.5, color='#74a65b', label='Potenza AC')
        ax.set_xlabel('Ora del giorno')
        ax.set_xticks(times[::max(1, len(times)//8)])
        ax.set_xticklabels(times[::max(1, len(times)//8)].strftime("%H:%M"), rotation=45)
        ax.set_ylabel('Potenza [W]')
        ax.set_title(f'Produzione - {comune} ({data})')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    # Grafico Irradianza
    with col_irr:
        fig2, ax2 = plt.subplots(figsize=(6,4))
        ax2.plot(times, clearsky['ghi'], label='GHI', color='#f39c12')
        ax2.plot(times, clearsky['dni'], label='DNI', color='#e74c3c')
        ax2.plot(times, poa['poa_global'], label='POA', color='#74a65b')
        ax2.set_xlabel('Ora del giorno')
        ax2.set_xticks(times[::max(1, len(times)//8)])
        ax2.set_xticklabels(times[::max(1, len(times)//8)].strftime("%H:%M"), rotation=45)
        ax2.set_ylabel('Irradianza [W/m²]')
        ax2.set_title('Irradianza Solare')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.legend()
        st.pyplot(fig2)
