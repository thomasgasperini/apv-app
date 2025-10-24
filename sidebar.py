"""
Modulo per la gestione della sidebar con input utente
Funzionalità:
- Header con logo
- Input localizzazione
- Input data simulazione
- Parametri pannello
- Parametri sistema elettrico
"""

from datetime import date
import streamlit as st
from geopy.geocoders import Nominatim
from config import DEFAULT_PARAMS, LOGO_URL, TIMEZONE_OBJ, HECTARE_M2, MESSAGES
from calculations import calculate_panel_area, calculate_coverage

# ==================== HEADER SIDEBAR ====================

def display_sidebar_header():
    """Visualizza logo nell'header della sidebar"""
    st.sidebar.markdown(f"""
    <div style="
        text-align:center;
        padding:1rem;
        margin-bottom:2rem;
        margin-top:-3rem;
        background: linear-gradient(135deg, #74a65b, #f9d71c);
        border-radius: 15px;
        overflow: hidden;
        height: 240px;
    ">
        <img src="{LOGO_URL}" 
             style="
                width:100%;
                height:auto;
                object-fit: cover;
                object-position: center bottom;
             ">
    </div>
    """, unsafe_allow_html=True)


# ==================== LOCALIZZAZIONE ====================

def get_location_from_comune(comune: str) -> tuple:
    """Geocodifica comune italiano"""
    try:
        geolocator = Nominatim(user_agent="pv_calculator_pro")
        location = geolocator.geocode(f"{comune}, Italia", timeout=10)
        if location:
            return location.latitude, location.longitude, location
    except Exception as e:
        st.sidebar.error(f"Errore geocoding: {e}")
    return None, None, None


def get_location_inputs() -> dict:
    """Raccoglie input di localizzazione"""
    with st.sidebar.expander("📍 Localizzazione", expanded=False):
        comune = st.text_input("Comune", value=DEFAULT_PARAMS["comune"])
        lat, lon, location = get_location_from_comune(comune)

        if lat is None or lon is None:
            st.warning(MESSAGES["location_not_found"])
            lat = st.number_input("Latitudine [°]", value=DEFAULT_PARAMS["lat"], format="%.4f")
            lon = st.number_input("Longitudine [°]", value=DEFAULT_PARAMS["lon"], format="%.4f")
            location = None
        else:
            st.success(MESSAGES["location_success"].format(lat=lat, lon=lon))

    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": TIMEZONE_OBJ,
        "location": location
    }


# ==================== DATA SIMULAZIONE ====================

def get_date_input() -> date:
    """Input data per la simulazione"""
    with st.sidebar.expander("📅 Data simulazione", expanded=False):
        return st.date_input("Seleziona data", value=date.today())


# ==================== PARAMETRI PANNELLO ====================

def get_panel_geometry() -> dict:
    """Input parametri geometrici e elettrici del pannello"""
    with st.sidebar.expander("🔧 Parametri pannello", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            num_panels = st.number_input(
                "Numero pannelli / ha", 
                value=DEFAULT_PARAMS["num_panels"], step=1, min_value=1
            )
            base = st.number_input(
                "Lato minore pannello [m]", 
                value=DEFAULT_PARAMS["base"], step=0.1, min_value=0.1
            )
            altezza_pannello = st.number_input(
                "Lato maggiore pannello [m]", 
                value=DEFAULT_PARAMS["altezza_pannello"], step=0.1, min_value=0.1
            )
            area = base * altezza_pannello

            st.markdown(f"""
                <div style="margin-bottom:0.6rem;">
                    <label style="font-weight:600;font-size:0.9rem;display:block;margin-bottom:0.2rem;">
                        Area pannello [m²]
                    </label>
                    <input type="text" value="{area:.2f}" readonly
                        style="background-color:#f0f2f6;
                               color:#000;
                               border:1px solid #ddd;
                               border-radius:0.5rem;
                               padding:0.4rem 0.5rem;
                               width:100%;
                               font-size:0.9rem;
                               cursor:default;">
                </div>
            """, unsafe_allow_html=True)

            altezza = st.number_input(
                "Altezza dal suolo [m]", value=DEFAULT_PARAMS["altezza"], step=0.1, min_value=0.1
            )

        with col2:
            tilt_pannello = st.slider("Tilt pannello [°]", 0, 90, DEFAULT_PARAMS["tilt"])
            azimuth_pannello = st.slider("Azimuth pannello [°]", -180, 180, DEFAULT_PARAMS["azimuth"])
            eff = st.number_input("Efficienza [%]", value=DEFAULT_PARAMS["eff"]*100, step=0.5, min_value=0.1, max_value=100.0) / 100
            temp_coeff = st.number_input("Coeff. temperatura γ [%/°C]", value=DEFAULT_PARAMS["temp_coeff"]*100, step=0.1)/100
            noct = st.number_input("NOCT [°C]", value=DEFAULT_PARAMS["noct"], step=1.0, min_value=20.0, max_value=60.0)

    return {
        "num_panels": num_panels,
        "base": base,
        "altezza_pannello": altezza_pannello,
        "area": area,
        "altezza": altezza,
        "tilt_pannello": tilt_pannello,
        "azimuth_pannello": azimuth_pannello,
        "eff": eff,
        "temp_coeff": temp_coeff,
        "noct": noct,
    }


# ==================== PARAMETRI SISTEMA ELETTRICO ====================

def get_electrical_parameters() -> dict:
    """Input parametri del sistema elettrico"""
    with st.sidebar.expander("⚡ Sistema elettrico", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            losses = st.number_input(
                "Perdite sistema [%]", value=DEFAULT_PARAMS["losses"]*100, step=1.0, min_value=0.0, max_value=50.0
            ) / 100
        with col2:
            albedo = st.number_input(
                "Albedo", value=DEFAULT_PARAMS["albedo"], step=0.05, min_value=0.0, max_value=1.0, format="%.2f"
            )
    return {"losses": losses, "albedo": albedo}


# ==================== PARAMETRI AGGIUNTIVI ====================

def get_additional_parameters() -> dict:
    """Input parametri aggiuntivi opzionali"""
    with st.sidebar.expander("🧩 Parametri aggiuntivi", expanded=False):
        extra_param = st.number_input("Parametro extra", value=0.0, step=0.1)
    return {"extra_param": extra_param}


# ==================== VALIDAZIONE ====================

def validate_and_display_status(panel_params: dict):
    """Valida la superficie effettiva e GCR"""
    superficie_effettiva, gcr = calculate_coverage(panel_params["num_panels"], panel_params["area"])
    is_valid = superficie_effettiva <= HECTARE_M2

    if not is_valid:
        max_panels = int(HECTARE_M2 // panel_params["area"])
        st.sidebar.warning(
            f"⚠️ Attenzione: superficie totale ({superficie_effettiva:.0f} m²) "
            f"supera 1 ettaro ({HECTARE_M2} m²)!\n"
            f"Numero massimo pannelli consentito: {max_panels}"
        )
    else:
        st.sidebar.success(MESSAGES["surface_valid"].format(
            superficie=superficie_effettiva, gcr=gcr
        ))

    return {
        "is_surface_valid": is_valid,
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr
    }


# ==================== FUNZIONE PRINCIPALE ====================

def sidebar_inputs() -> dict:
    """Raccoglie tutti gli input dalla sidebar e li valida"""
    display_sidebar_header()
    location_data = get_location_inputs()
    data = get_date_input()
    panel_params = get_panel_geometry()
    electrical_params = get_electrical_parameters()
    additional_params = get_additional_parameters()
    validation_results = validate_and_display_status(panel_params)

    # Unione di tutti i parametri
    return {
        **location_data,
        "data": data,
        **panel_params,
        **electrical_params,
        **additional_params,
        **validation_results
    }
