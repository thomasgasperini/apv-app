import streamlit as st
from datetime import date
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim

def sidebar_inputs():
    # Logo centrato in alto senza margini
    st.sidebar.markdown("""
    <style>
        /* Rimuove padding superiore della sidebar */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }
        /* Stile per il container del logo */
        .logo-container {
            text-align: center;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #74a65b 0%, #f7e08e 100%);
            border-radius: 8px;
            padding: 1.5rem 0.5rem;
            margin-bottom: 1.5rem;
        }
        /* Migliora la leggibilità degli expander */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1.05rem;
        }
        /* Successo personalizzato */
        .stSuccess {
            padding: 0.5rem;
            font-size: 0.9rem;
        }
    </style>
    <div class="logo-container">
        <img src="http://www.resfarm.it/wp-content/uploads/2025/02/Logo_Resfarm_home_white.svg#121" 
             style="max-width: 85%; height: auto;">
    </div>
    """, unsafe_allow_html=True)

    # Titolo sidebar compatto
    st.sidebar.markdown("### ⚙️ Configurazione Simulatore")

    # Localizzazione
    with st.sidebar.expander("📍 **Localizzazione**", expanded=True):
        comune = st.text_input("Comune", value="Roma", help="Nome del comune italiano", label_visibility="collapsed", placeholder="🏙️ Inserisci il comune...")
        
        geolocator = Nominatim(user_agent="pv_calculator_pro")
        location = geolocator.geocode(f"{comune}, Italia", timeout=10)

        if location:
            lat = location.latitude
            lon = location.longitude
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

    # Parametri pannello
    with st.sidebar.expander("🔧 **Parametri Pannello**", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            tilt = st.slider("Inclinazione [°]", 0, 90, 30, help="Angolo β rispetto all'orizzontale")
            area = st.number_input("Area [m²]", value=1.6, step=0.1, format="%.2f")
        with col2:
            azimuth = st.slider("Azimut [°]", -180, 180, 0, help="0°=Sud, -90°=Est, +90°=Ovest")
            eff = st.number_input("Efficienza [%]", value=20.0, step=0.5, format="%.1f") / 100
        
        col3, col4 = st.columns(2)
        with col3:
            noct = st.number_input("NOCT [°C]", value=45.0, format="%.1f")
        with col4:
            temp_coeff = st.number_input("γ [%/°C]", value=-0.4, step=0.1, format="%.2f") / 100

    # Sistema elettrico
    with st.sidebar.expander("⚡ **Sistema Elettrico**", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            losses = st.number_input("Perdite [%]", value=10.0, step=1.0, format="%.1f") / 100
        with col2:
            albedo = st.number_input("Albedo", value=0.2, step=0.05, format="%.2f", help="Riflettività 0-1")

    # Data
    with st.sidebar.expander("📅 **Data Simulazione**", expanded=False):
        data = st.date_input("Seleziona data", value=date(2025, 6, 21), label_visibility="collapsed")
        st.caption(f"🗓️ {data.strftime('%d/%m/%Y')}")

    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": timezone,
        "tilt": tilt,
        "azimuth": azimuth,
        "area": area,
        "eff": eff,
        "noct": noct,
        "temp_coeff": temp_coeff,
        "losses": losses,
        "albedo": albedo,
        "data": data,
        "location": location
    }