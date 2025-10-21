# sidebar_inputs.py
from datetime import date
import streamlit as st
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim

def sidebar_inputs():
    """
    Sidebar per configurare tutti i parametri della simulazione fotovoltaica.
    Le voci ora includono spiegazioni chiare sul significato fisico e sul ruolo
    di ciascun parametro.
    """
    # --- Logo e stile ---
    st.sidebar.markdown("""
    <style>
        [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
        .logo-container {
            text-align: center;
            margin: 0;
            padding: 1.5rem 0.5rem;
            background: linear-gradient(135deg, #74a65b 0%, #f7e08e 100%);
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        .streamlit-expanderHeader { font-weight: 600; font-size: 1.05rem; }
        .stSuccess { padding: 0.5rem; font-size: 0.9rem; }
    </style>
    <div class="logo-container">
        <img src="http://www.resfarm.it/wp-content/uploads/2025/02/Logo_Resfarm_home_white.svg#121" 
             style="max-width: 85%; height: auto;">
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### ⚙️ Configurazione Simulatore")

    # --- Localizzazione ---
    with st.sidebar.expander("📍 Localizzazione", expanded=True):
        comune = st.text_input(
            "Comune", value="Roma", placeholder="🏙️ Inserisci il comune..."
        )
        geolocator = Nominatim(user_agent="pv_calculator_pro")
        location = geolocator.geocode(f"{comune}, Italia", timeout=10)

        if location:
            lat, lon = location.latitude, location.longitude
            timezone = ZoneInfo("Europe/Rome")
            st.success(f"📌 {lat:.4f}°N, {lon:.4f}°E")
        else:
            st.error("⚠️ Comune non trovato")
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Lat [°]", value=41.9, format="%.2f")
            with col2:
                lon = st.number_input("Lon [°]", value=12.5, format="%.2f")
            timezone = ZoneInfo("Europe/Rome")

    # --- Data simulazione ---
    with st.sidebar.expander("📅 Data simulazione", expanded=True):
        data = st.date_input("Seleziona data", value=date.today())
        st.caption(f"🗓️ {data.strftime('%d/%m/%Y')}")

    # --- Parametri pannello ---
    with st.sidebar.expander("🔧 Parametri pannello", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            num_panels = st.number_input(
                "Numero pannelli / ha", value=625, step=1,
                help="Numero di pannelli installati su 1 ettaro. Influisce sulla superficie totale e sul rischio di ombreggiamento tra pannelli.")
            area = st.number_input(
                "Area pannello [m²]", value=1.6, step=0.1,
                help="Superficie di un singolo pannello; maggiore area → più energia catturata.")
            altezza = st.number_input(
                "Altezza dal suolo [m]", value=1.0, step=0.1,
                help="Distanza centrale del pannello dal terreno; influenza ombreggiamento e radiazione al suolo.")
            pitch_laterale = st.number_input(
                "Distanza laterale tra pannelli [m]", value=1.3, step=0.05,
                help="Spazio tra pannelli nella stessa fila; maggiore distanza → meno ombreggiamento laterale.")
            pitch_file = st.number_input(
                "Distanza tra file parallele [m]", value=2.0, step=0.05,
                help="Spazio tra file parallele; maggiore distanza riduce ombreggiamento tra file.")

        with col2:
            tilt = st.slider(
                "Tilt [°]", 0, 90, 30,
                help="Inclinazione del pannello rispetto al piano orizzontale. Influisce sull’angolo di incidenza del sole e quindi sulla produzione di energia."
            )
            azimuth = st.slider(
                "Azimuth [°]", -180, 180, 0,
                help="Orientamento dei pannelli rispetto al Nord (0° = Nord, 180° = Sud). Determina la distribuzione giornaliera della produzione."
            )
            temp_coeff = st.number_input(
                "γ [%/°C]", value=-0.4, step=0.1,
                help="Coefficiente di temperatura: riduce l’efficienza del modulo quando la temperatura aumenta."
            ) / 100
            eff = st.number_input(
                "Efficienza [%]", value=20.0, step=0.5,
                help="Efficienza nominale del modulo: percentuale di energia solare convertita in elettricità."
            ) / 100
            noct = st.number_input(
                "NOCT [°C]", value=45.0,
                help="Temperatura nominale operativa della cella in condizioni standard. Influisce sulla temperatura reale della cella durante il funzionamento."
            )

        # Calcolo superficie occupata usando pitch
        superficie_totale = num_panels * pitch_laterale * pitch_file
        if superficie_totale > 10000:
            st.warning(
                f"⚠️ La superficie totale ({superficie_totale:.0f} m²) supera 1 ettaro. Riduci numero pannelli o aumenta distanze."
            )

    # --- Sistema elettrico ---
    with st.sidebar.expander("⚡ Sistema elettrico", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            losses = st.number_input(
                "Perdite [%]", value=10.0, step=1.0)/100
            st.caption("Perdite complessive dell’impianto: inverter, cablaggi, mismatch, ombreggiamento, polvere, ecc.")
        with col2:
            albedo = st.number_input(
                "Albedo", value=0.2, step=0.05)
            st.caption("Fraz. di radiazione riflessa dal terreno che può contribuire alla radiazione sul pannello.")

    # --- Parametri aggiuntivi ---
    with st.sidebar.expander("🧩 Parametri aggiuntivi", expanded=False):
        extra_param = st.number_input("Param extra", value=0.0)

    # --- Ritorno dei valori ---
    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": timezone,
        "data": data,
        "tilt": tilt,
        "azimuth": azimuth,
        "area": area,
        "num_panels": num_panels,
        "altezza": altezza,
        "pitch_laterale": pitch_laterale,
        "pitch_file": pitch_file,
        "eff": eff,
        "noct": noct,
        "temp_coeff": temp_coeff,
        "losses": losses,
        "albedo": albedo,
        "extra_param": extra_param,
        "location": location
    }
