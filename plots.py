import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import screeninfo

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

    # Prepara le card
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

    # Responsive: 4 colonne su desktop, 2 su tablet, 1 su mobile
    width = st.columns([1]*4)
    if st.runtime.exists():  # fallback: semplicemente mostra in colonna su mobile
        try:
            from screeninfo import get_monitors
            screen_width = get_monitors()[0].width
        except:
            screen_width = 1200  # default desktop

    if screen_width > 1024:  # desktop
        cols = st.columns(4)
        for c, card in zip(cols, metric_cards):
            c.markdown(card, unsafe_allow_html=True)
    elif screen_width > 600:  # tablet
        for i in range(0, 4, 2):
            cols = st.columns(2)
            for c, card in zip(cols, metric_cards[i:i+2]):
                c.markdown(card, unsafe_allow_html=True)
    else:  # mobile
        for card in metric_cards:
            st.markdown(card, unsafe_allow_html=True)

    # -----------------------
    # 🗺️ Mappa Interattiva
    # -----------------------
    if location:
        st.markdown('<p class="section-header">📍 Localizzazione Impianto</p>', unsafe_allow_html=True)
        col_map, col_info = st.columns([2, 1])

        # Altezza mappa adattiva
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
    # 📈 Grafici affiancati: Produzione & Irradianza
    # -----------------------
    st.markdown('<p class="section-header">📈 Analisi Dettagliata</p>', unsafe_allow_html=True)

    # Adatta grafici: due colonne su desktop/tablet, stacking su mobile
    if screen_width > 768:
        col_prod, col_irr = st.columns(2)
    else:
        col_prod = col_irr = st.container()  # stacking verticale

    # Grafico Produzione
    with col_prod:
        fig, ax = plt.subplots(figsize=(max(4, min(6, screen_width/200)), 4))
        ax.fill_between(times, P_ac, alpha=0.3, color='#74a65b')
        ax.plot(times, P_ac, linewidth=2.5, color='#74a65b', label='Potenza AC')
        ax.set_xlabel('Ora del giorno')
        step = max(1, len(times)//8)
        ax.set_xticks(times[::step])
        ax.set_xticklabels(times[::step].strftime("%H:%M"), rotation=45)
        ax.set_ylabel('Potenza [W]')
        ax.set_title(f'Produzione - {comune} ({data})')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    # Grafico Irradianza
    with col_irr:
        fig2, ax2 = plt.subplots(figsize=(max(4, min(6, screen_width/200)), 4))
        ax2.plot(times, clearsky['ghi'], label='GHI', color='#f39c12')
        ax2.plot(times, clearsky['dni'], label='DNI', color='#e74c3c')
        ax2.plot(times, poa['poa_global'], label='POA', color='#74a65b')
        ax2.set_xlabel('Ora del giorno')
        ax2.set_xticks(times[::step])
        ax2.set_xticklabels(times[::step].strftime("%H:%M"), rotation=45)
        ax2.set_ylabel('Irradianza [W/m²]')
        ax2.set_title('Irradianza Solare')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.legend()
        st.pyplot(fig2)
