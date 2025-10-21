import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from datetime import datetime

# -----------------------
# Configurazione pagina
# -----------------------
st.set_page_config(
    page_title="Analisi Produzione Fotovoltaico",
    layout="wide"
)

# -----------------------
# Funzione principale per plottare i risultati
# -----------------------
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

    # Tentativo di rilevare la larghezza dello schermo
    try:
        from screeninfo import get_monitors
        screen_width = get_monitors()[0].width
    except:
        screen_width = 1200  # fallback desktop

    # -----------------------
    # ⚡ Risultati principali (card HTML/CSS)
    # -----------------------
    st.markdown('<p class="section-header">⚡ Risultati di Produzione</p>', unsafe_allow_html=True)

    metric_cards = [
        f"""
        <div class="metric-card">
            <div class="metric-label">Energia Giornaliera</div>
            <div class="metric-value">{results['E_day']:.2f} kWh</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">Picco di Potenza</div>
            <div class="metric-value">{P_ac.max():.0f} W</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">Irradianza Max</div>
            <div class="metric-value">{poa['poa_global'].max():.0f} W/m²</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">Energia Annuale Est.</div>
            <div class="metric-value">{results['E_day']*365:.0f} kWh</div>
        </div>
        """
    ]

    # Distribuzione responsive delle card
    if screen_width > 1024:  # desktop → 4 colonne
        cols = st.columns(4, gap="medium")
        for c, card in zip(cols, metric_cards):
            c.markdown(card, unsafe_allow_html=True)
    elif screen_width > 600:  # tablet → 2 colonne
        for i in range(0, 4, 2):
            cols = st.columns(2, gap="medium")
            for c, card in zip(cols, metric_cards[i:i+2]):
                c.markdown(card, unsafe_allow_html=True)
    else:  # mobile → 1 colonna
        for card in metric_cards:
            st.markdown(card, unsafe_allow_html=True)

    # -----------------------
    # 🗺️ Mappa Interattiva + Info
    # -----------------------
    if location:
        st.markdown('<p class="section-header">📍 Localizzazione Impianto</p>', unsafe_allow_html=True)

        col_map, col_info = st.columns([3, 1], gap="medium")  # map più grande, info laterale

        height_map = 300 if screen_width <= 480 else 400

        with col_map:
            m = folium.Map(location=[lat, lon], zoom_start=6, tiles='Cartodb Positron')
            folium.Marker(
                [lat, lon],
                tooltip=comune,
                popup=f"<b>{comune}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
                icon=folium.Icon(color='green', icon='sun', prefix='fa')
            ).add_to(m)
            st_folium(m, width="100%", height=height_map)

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
        # 📈 Grafici Produzione & Irradianza in unica figura
        # -----------------------
        st.markdown('<p class="section-header">📈 Analisi Dettagliata</p>', unsafe_allow_html=True)

        # Stacking su mobile, affiancati su desktop/tablet
        if screen_width > 768:
            container = st.container()
        else:
            container = st.container()

        # Definiamo dimensione unica della figura
        fig_width = max(10, min(14, screen_width / 100))  # larghezza totale
        fig_height = 4  # stessa altezza per entrambi

        # Creiamo subplot affiancati
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height), constrained_layout=True)

        # -----------------------
        # Grafico Produzione
        # -----------------------
        ax1.fill_between(times, P_ac, alpha=0.3, color='#74a65b')
        ax1.plot(times, P_ac, linewidth=2.5, color='#74a65b', label='Potenza AC')
        ax1.set_xlabel('Ora del giorno')
        ax1.set_ylabel('Potenza [W]')
        ax1.set_title(f'Produzione - {comune} ({data})')
        ax1.grid(True, linestyle='--', alpha=0.3)
        ax1.legend()
        step = max(1, len(times)//8)
        ax1.set_xticks(times[::step])
        ax1.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)

        # -----------------------
        # Grafico Irradianza
        # -----------------------
        ax2.plot(times, clearsky['ghi'], label='GHI', color='#f39c12')
        ax2.plot(times, clearsky['dni'], label='DNI', color='#e74c3c')
        ax2.plot(times, poa['poa_global'], label='POA', color='#74a65b')
        ax2.set_xlabel('Ora del giorno')
        ax2.set_ylabel('Irradianza [W/m²]')
        ax2.set_title('Irradianza Solare')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.legend()
        ax2.set_xticks(times[::step])
        ax2.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)

        # Mostriamo la figura in Streamlit
        st.pyplot(fig, use_container_width=True)
