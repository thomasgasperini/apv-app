import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

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
    # --- Estrazione dati principali ---
    times = results["times"]
    P_ac = results["P_ac"]
    poa = results["poa"]
    clearsky = results["clearsky"]
    E_suolo = results.get("E_suolo")  
    comune = params["comune"]
    data = params["data"]
    lat = params["lat"]
    lon = params["lon"]
    location = params.get("location", None)
    
    superficie_effettiva = params['num_panels'] * params['pitch_laterale'] * params['pitch_file']

    # --- Rilevamento larghezza schermo per layout responsive ---
    try:
        from screeninfo import get_monitors
        screen_width = get_monitors()[0].width
    except:
        screen_width = 1200  # fallback

    # -----------------------
    # 🗺️ Mappa Interattiva + Info
    # -----------------------
    if location:
        st.markdown('<p class="section-header">📍 Localizzazione Impianto</p>', unsafe_allow_html=True)
        col_map, col_info = st.columns([3, 1], gap="medium")
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
            <div class="formula-box">
                <div class="formula-title">🧭 Orientamento Pannelli</div>
                Inclinazione (β): <b>{params['tilt']}°</b><br>
                Azimut: <b>{params['azimuth']}°</b><br>
                Albedo: <b>{params['albedo']:.2f}</b>
            </div>
            """, unsafe_allow_html=True)

    # -----------------------
    # ⚡ Risultati principali: Card con logica chiara
    # -----------------------
    st.markdown('<p class="section-header">⚡ Risultati Produzione & Agro-FV</p>', unsafe_allow_html=True)

    metric_cards = [
        # 🌞 Energia solare incidente
        f"""
        <div class="metric-card">
            <div class="metric-label">🌞 GHI Totale</div>
            <div class="metric-value">{clearsky['ghi'].sum()/1000:.2f} kWh/m²</div>
            <div class="metric-description">Radiazione globale orizzontale sul sito, senza pannelli.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">🌞 DNI Totale</div>
            <div class="metric-value">{clearsky['dni'].sum()/1000:.2f} kWh/m²</div>
            <div class="metric-description">Radiazione diretta dal sole perpendicolare ai raggi.</div>
        </div>
        """,

        # ⚡ Energia prodotta dai pannelli
        f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Energia Giornaliera Pannelli</div>
            <div class="metric-value">{results['E_day']:.2f} kWh/ha</div>
            <div class="metric-description">Energia elettrica generata dai pannelli (giornaliera).</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Picco Potenza AC</div>
            <div class="metric-value">{P_ac.max():.0f} W</div>
            <div class="metric-description">Potenza massima istantanea dei pannelli.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">⚡ POA Totale</div>
            <div class="metric-value">{poa['poa_global'].sum()/1000:.2f} kWh/m²</div>
            <div class="metric-description">Radiazione sul piano dei pannelli (tilt/azimuth).</div>
        </div>
        """,

        # 🌱 Agro-FV
        f"""
        <div class="metric-card">
            <div class="metric-label">🌱 Energia suolo tra pannelli</div>
            <div class="metric-value">{results['E_suolo_tot']:.2f} kWh/ha</div>
            <div class="metric-description">Radiazione che raggiunge il terreno tra i pannelli.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">🌱 Frazione suolo illuminata</div>
            <div class="metric-value">{results['f_luce']*100:.1f} %</div>
            <div class="metric-description">Percentuale di terreno non ombreggiato dai pannelli.</div>
        </div>
        """,

        # 📏 Parametri geometrici
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Area Totale Pannelli</div>
            <div class="metric-value">{params['num_panels']*params['area']:.0f} m²</div>
            <div class="metric-description">Superficie fisica dei pannelli installati.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Superficie Effettiva Occupata</div>
            <div class="metric-value">{superficie_effettiva:.0f} m²</div>
            <div class="metric-description">Area complessiva inclusi spazi tra file.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Land Area Occupation Ratio</div>
            <div class="metric-value">{results['fattore_copertura']*100:.1f} %</div>
            <div class="metric-description">Rapporto tra pannelli e area totale del sito.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Pitch (Laterale / File)</div>
            <div class="metric-value">{params['pitch_laterale']:.2f} m / {params['pitch_file']:.2f} m</div>
            <div class="metric-description">Distanza tra pannelli e tra file.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Tilt / Azimuth</div>
            <div class="metric-value">{params['tilt']}° / {params['azimuth']}°</div>
            <div class="metric-description">Inclinazione e orientamento dei pannelli.</div>
        </div>
        """,
        f"""
        <div class="metric-card">
            <div class="metric-label">📏 Albedo / Perdite</div>
            <div class="metric-value">{params['albedo']:.2f} / {params['losses']*100:.1f} %</div>
            <div class="metric-description">Riflettanza del terreno e perdite complessive impianto.</div>
        </div>
        """
    ]

    # --- Layout responsivo ---
    if screen_width > 1200:
        cols = st.columns(5, gap="medium")
        for i, card in enumerate(metric_cards):
            cols[i%5].markdown(card, unsafe_allow_html=True)
    elif screen_width > 768:
        cols = st.columns(2, gap="medium")
        for i in range(0, len(metric_cards), 2):
            for c, card in zip(cols, metric_cards[i:i+2]):
                c.markdown(card, unsafe_allow_html=True)
    else:
        for card in metric_cards:
            st.markdown(card, unsafe_allow_html=True)

    # -----------------------
    # 📈 Grafici Produzione & Irradianza
    # -----------------------
    st.markdown('<p class="section-header">📈 Analisi Dettagliata</p>', unsafe_allow_html=True)
    fig_width = max(10, min(14, screen_width / 100))
    fig_height = 4
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height), constrained_layout=True)

    # --- ⚡ Grafico Potenza AC ---
    ax1.fill_between(times, P_ac, alpha=0.3, color='#74a65b')
    ax1.plot(times, P_ac, linewidth=2.5, color='#74a65b', label='⚡ Potenza AC Pannelli')
    ax1.set_xlabel('Ora del giorno')
    ax1.set_ylabel('Potenza [W]')
    ax1.set_title(f'Produzione Elettrica - {comune} ({data})')
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend()
    step = max(1, len(times)//8)
    ax1.set_xticks(times[::step])
    ax1.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)

    # --- 🌞 Grafico Irradianza ---
    ax2.plot(times, clearsky['ghi'], label='🌞 GHI Orizzontale', color='#f39c12', linewidth=1.5)
    ax2.plot(times, clearsky['dni'], label='🌞 DNI Diretta', color='#e74c3c', linewidth=1.5)
    ax2.plot(times, poa['poa_global'], label='⚡ POA sul Pannello', color='#74a65b', linewidth=1.5)
    if E_suolo is not None:
        ax2.plot(times, E_suolo, label='🌱 Radiazione suolo', color='#3498db', linestyle='--', linewidth=2)

    ax2.set_xlabel('Ora del giorno')
    ax2.set_ylabel('Irradianza [W/m²]')
    ax2.set_title('Irradianza Solare e Agro-FV')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.legend()
    ax2.set_xticks(times[::step])
    ax2.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)

    st.pyplot(fig, use_container_width=True)
