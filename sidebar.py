# sidebar.py
"""
Modulo per la gestione degli input utente dalla sidebar
"""

from datetime import date
import streamlit as st
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from config import DEFAULT_PARAMS, LOGO_URL, TIMEZONE, MESSAGES, HECTARE_M2


def display_sidebar_header():
    """Visualizza header con logo nella sidebar"""
    st.sidebar.markdown(f"""
    <style>
        [data-testid="stSidebar"] > div:first-child {{ padding-top: 1rem; }}
        .logo-container {{
            text-align: center;
            margin: 0;
            padding: 1.5rem 0.5rem;
            background: linear-gradient(135deg, #74a65b 0%, #f7e08e 100%);
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }}
        .streamlit-expanderHeader {{ font-weight: 600; font-size: 1.05rem; }}
        .stSuccess {{ padding: 0.5rem; font-size: 0.9rem; }}
    </style>
    <div class="logo-container">
        <img src="{LOGO_URL}" style="max-width: 85%; height: auto;">
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### ⚙️ Configurazione Simulatore")


def get_location_inputs():
    """Gestisce input localizzazione"""
    with st.sidebar.expander("📍 Localizzazione", expanded=True):
        comune = st.text_input(
            "Comune", 
            value=DEFAULT_PARAMS["comune"], 
            placeholder="🏙️ Inserisci il comune..."
        )
        
        geolocator = Nominatim(user_agent="pv_calculator_pro")
        location = geolocator.geocode(f"{comune}, Italia", timeout=10)

        if location:
            lat, lon = location.latitude, location.longitude
            timezone = ZoneInfo(TIMEZONE)
            st.success(MESSAGES["location_success"].format(lat=lat, lon=lon))
        else:
            st.error(MESSAGES["location_not_found"])
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Lat [°]", value=DEFAULT_PARAMS["lat"], format="%.2f")
            with col2:
                lon = st.number_input("Lon [°]", value=DEFAULT_PARAMS["lon"], format="%.2f")
            timezone = ZoneInfo(TIMEZONE)
            location = None
    
    return comune, lat, lon, timezone, location


def get_date_input():
    """Gestisce input data"""
    with st.sidebar.expander("📅 Data simulazione", expanded=True):
        data = st.date_input("Seleziona data", value=date.today())
        st.caption(f"🗓️ {data.strftime('%d/%m/%Y')}")
    return data


def get_panel_parameters():
    """Gestisce parametri pannello"""
    with st.sidebar.expander("🔧 Parametri pannello", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            num_panels = st.number_input(
                "Numero pannelli / ha", 
                value=DEFAULT_PARAMS["num_panels"], 
                step=1,
                help="Numero di pannelli installati su 1 ettaro. Influisce sulla superficie totale e sul rischio di ombreggiamento tra pannelli."
            )
            area = st.number_input(
                "Area pannello [m²]", 
                value=DEFAULT_PARAMS["area"], 
                step=0.1,
                help="Superficie di un singolo pannello; maggiore area → più energia catturata."
            )
            altezza = st.number_input(
                "Altezza dal suolo [m]", 
                value=DEFAULT_PARAMS["altezza"], 
                step=0.1,
                help="Distanza centrale del pannello dal terreno; influenza ombreggiamento e radiazione al suolo."
            )
            pitch_laterale = st.number_input(
                "Distanza laterale tra pannelli [m]", 
                value=DEFAULT_PARAMS["pitch_laterale"], 
                step=0.05,
                help="Spazio tra pannelli nella stessa fila; maggiore distanza → meno ombreggiamento laterale."
            )
            pitch_file = st.number_input(
                "Distanza tra file parallele [m]", 
                value=DEFAULT_PARAMS["pitch_file"], 
                step=0.05,
                help="Spazio tra file parallele; maggiore distanza riduce ombreggiamento tra file."
            )

        with col2:
            tilt = st.slider(
                "Tilt [°]", 0, 90, DEFAULT_PARAMS["tilt"],
                help="Inclinazione del pannello rispetto al piano orizzontale. Influisce sull'angolo di incidenza del sole e quindi sulla produzione di energia."
            )
            azimuth = st.slider(
                "Azimuth [°]", -180, 180, DEFAULT_PARAMS["azimuth"],
                help="Orientamento dei pannelli rispetto al Nord (0° = Nord, 180° = Sud). Determina la distribuzione giornaliera della produzione."
            )
            temp_coeff = st.number_input(
                "γ [%/°C]", 
                value=DEFAULT_PARAMS["temp_coeff"]*100, 
                step=0.1,
                help="Coefficiente di temperatura: riduce l'efficienza del modulo quando la temperatura aumenta."
            ) / 100
            eff = st.number_input(
                "Efficienza [%]", 
                value=DEFAULT_PARAMS["eff"]*100, 
                step=0.5,
                help="Efficienza nominale del modulo: percentuale di energia solare convertita in elettricità."
            ) / 100
            noct = st.number_input(
                "NOCT [°C]", 
                value=DEFAULT_PARAMS["noct"],
                help="Temperatura nominale operativa della cella in condizioni standard. Influisce sulla temperatura reale della cella durante il funzionamento."
            )

        # Validazione superficie
        superficie_totale = num_panels * pitch_laterale * pitch_file
        if superficie_totale > HECTARE_M2:
            st.warning(MESSAGES["surface_warning"].format(superficie=superficie_totale))
    
    return {
        "num_panels": num_panels,
        "area": area,
        "altezza": altezza,
        "pitch_laterale": pitch_laterale,
        "pitch_file": pitch_file,
        "tilt": tilt,
        "azimuth": azimuth,
        "temp_coeff": temp_coeff,
        "eff": eff,
        "noct": noct,
    }


def get_electrical_parameters():
    """Gestisce parametri sistema elettrico"""
    with st.sidebar.expander("⚡ Sistema elettrico", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            losses = st.number_input(
                "Perdite [%]", 
                value=DEFAULT_PARAMS["losses"]*100, 
                step=1.0
            ) / 100
            st.caption("Perdite complessive dell'impianto: inverter, cablaggi, mismatch, ombreggiamento, polvere, ecc.")
        with col2:
            albedo = st.number_input(
                "Albedo", 
                value=DEFAULT_PARAMS["albedo"], 
                step=0.05
            )
            st.caption("Fraz. di radiazione riflessa dal terreno che può contribuire alla radiazione sul pannello.")
    
    return losses, albedo


def get_additional_parameters():
    """Gestisce parametri aggiuntivi"""
    with st.sidebar.expander("🧩 Parametri aggiuntivi", expanded=False):
        extra_param = st.number_input("Param extra", value=0.0)
    return extra_param


def sidebar_inputs():
    """
    Funzione principale che raccoglie tutti gli input dalla sidebar
    """
    display_sidebar_header()
    
    # Localizzazione
    comune, lat, lon, timezone, location = get_location_inputs()
    
    # Data
    data = get_date_input()
    
    # Parametri pannello
    panel_params = get_panel_parameters()
    
    # Sistema elettrico
    losses, albedo = get_electrical_parameters()
    
    # Parametri aggiuntivi
    extra_param = get_additional_parameters()
    
    # Ritorna dizionario completo
    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": timezone,
        "data": data,
        "location": location,
        "losses": losses,
        "albedo": albedo,
        "extra_param": extra_param,
        **panel_params,
    }
