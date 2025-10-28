"""
Modulo sidebar con input utente
- Logo
- Localizzazione + data simulazione
- Parametri pannello
- Sistema elettrico
- Parametri aggiuntivi
"""

from datetime import date
import streamlit as st
from geopy.geocoders import Nominatim
from config import DEFAULT_PARAMS, LOGO_URL, TIMEZONE_OBJ, HECTARE_M2, MESSAGES
from calculations import calculate_coverage

# ==================== HEADER ====================
def display_sidebar_header():
    st.sidebar.markdown(f"""
    <style>
        section[data-testid="stSidebar"] button[kind="icon"],
        section[data-testid="stSidebar"] [role="button"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {{
            position: relative !important;
            top: 1rem !important;
            right: 1rem !important;
            z-index: 9999 !important;
            pointer-events: auto !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        .sidebar-header-logo {{
            position: relative;
            z-index: 1;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #74a65b, #f9d71c);
            border-radius: 15px;
            padding: 1rem;
            margin-top: -4rem;
            margin-bottom: -1rem;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .sidebar-header-logo img {{
            width: 100%;
            height: auto;
            max-height: 25vh;
            object-fit: contain;
            object-position: center;
            border-radius: 5px;
        }}
        @media (max-height: 700px) {{
            .sidebar-header-logo img {{
                max-height: 18vh;
            }}
        }}
    </style>
    <div class="sidebar-header-logo">
        <img src="{LOGO_URL}" alt="Logo">
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style='text-align:center; margin-bottom:0rem;'>Interfaccia INPUT</h3>", unsafe_allow_html=True)

# ==================== LOCALIZZAZIONE ====================
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from datetime import date
import time

def get_location_from_comune(comune: str, max_retries: int = 10):
    """Tenta di ottenere lat/lon da Nominatim. Riprova alcune volte se fallisce."""
    geolocator = Nominatim(user_agent="pv_calculator_pro", timeout=15)

    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(f"{comune}, Italia")
            if location:
                return location.latitude, location.longitude, location
        except (GeocoderServiceError, GeocoderTimedOut):
            time.sleep(1.5 * (attempt + 1))  # backoff progressivo
        except Exception as e:
            st.sidebar.warning(f"⚠️ Errore geocoding: {e}")
            break

    # Se non è riuscito a connettersi o trovare la posizione
    return None, None, None


def get_location_and_date_inputs():
    with st.sidebar.expander("🌍 Localizzazione e Data simulazione", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            comune = st.text_input("Comune", value=DEFAULT_PARAMS["comune"])

            # Tentativo di geocoding
            lat, lon, location = get_location_from_comune(comune)

        with col2:
            data_simulazione = st.date_input("📅 Seleziona data", value=date.today())

       
        st.success(f"📍 Coordinate: lat {lat:.4f}, lon {lon:.4f}")
    if lat is None or lon is None:
        st.info("🌐 Nessuna connessione o località non trovata. Inserisci manualmente le coordinate (lat, lon).")
        lat = st.number_input(
                    "Latitudine [°]", 
                    value=DEFAULT_PARAMS["lat"], 
                    format="%.4f"
                )
        lon = st.number_input(
                    "Longitudine [°]", 
                    value=DEFAULT_PARAMS["lon"], 
                    format="%.4f"
                )
        location = None
    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": TIMEZONE_OBJ,
        "location": location,
        "data": data_simulazione
    }

# ==================== PARAMETRI PANNELLO ====================
def get_panel_geometry():
    with st.sidebar.expander("🔧 Parametri pannello", expanded=False):

        # ===== DEFAULT PARAMETERS =====
        DEFAULT_PARAMS = {
            "num_panels": 1,            # int
            "base_pannello": 2.0,       # float
            "altezza_pannello": 2.5,    # float
            "altezza_suolo": 1.0,       # float
            "tilt": 30,                 # int
            "azimuth": 180,             # int
            "eff": 0.18,                # float (0-1)
            "temp_coeff": -0.004,       # float
            "noct": 45                  # float
        }

        # ================== RIGA 1 ==================
        col1, col2 = st.columns(2)
        num_panels = col1.number_input(
            "Numero pannelli / ha",
            value=int(DEFAULT_PARAMS["num_panels"]),
            step=1,
            min_value=0
        )
        pannelli_per_fila = col2.number_input(
            "Pannelli per fila",
            value=int(1),
            step=1,
            min_value=1,
            max_value=num_panels
        )
        num_file = (num_panels + pannelli_per_fila - 1) // pannelli_per_fila
        if num_panels < 2:
            st.sidebar.info("Consigliato almeno 2 pannelli per una migliore simulazione.")

        # ================== RIGA 2 ==================
        col1, col2 = st.columns(2)
        base_pannello = col1.number_input(
            "Lato < pannello [m]",
            value=float(DEFAULT_PARAMS["base_pannello"]),
            step=0.1,
            min_value=0.1
        )
        altezza_pannello = col2.number_input(
            "Lato > pannello [m]",
            value=float(DEFAULT_PARAMS["altezza_pannello"]),
            step=0.1,
            min_value=0.1
        )

        # ================== RIGA 3 ==================
        col1, col2 = st.columns(2)
        pitch_laterale = col1.number_input(
            "Pitch laterale [m]",
            step=0.1,
            min_value=0.0
        )
        pitch_verticale = col2.number_input(
            "Pitch verticale [m]",
            step=0.1,
            min_value=0.0
        )

        # ================== RIGA 4 ==================
        col1, col2 = st.columns(2)
        area = col1.text_input(
            "Area pannello [m²]",
            value=f"{base_pannello*altezza_pannello:.2f}",
            disabled=True
        )
        altezza_suolo = col2.number_input(
            "Altezza dal suolo [m]",
            value=float(DEFAULT_PARAMS["altezza_suolo"]),
            step=0.1,
            min_value=0.1
        )

        # ================== RIGA 5 ==================
        col1, col2, col3 = st.columns(3)
        tilt = col1.slider(
            "Tilt pannello [°]",
            min_value=0,
            max_value=90,
            value=int(DEFAULT_PARAMS["tilt"])
        )
        azimuth = col2.slider(
            "Azimuth pannello [°]",
            min_value=0,
            max_value=360,
            value=int(DEFAULT_PARAMS["azimuth"])
        )

        # ================== RIGA 6 ==================
        col1, col2 = st.columns(2)
        eff = col1.number_input(
            "Efficienza [%]",
            value=float(DEFAULT_PARAMS["eff"]*100),
            step=0.5,
            min_value=0.1,
            max_value=100.0
        )/100
        temp_coeff = col2.number_input(
            "Coeff. γ [%/°C]",
            value=float(DEFAULT_PARAMS["temp_coeff"]*100),
            step=0.1
        )/100

        # ================== RIGA 7 ==================
        noct = st.number_input(
            "NOCT [°C]",
            value=float(DEFAULT_PARAMS["noct"]),
            step=1.0,
            min_value=20.0,
            max_value=60.0
        )


    return {
        "num_panels": num_panels,
        "pannelli_per_fila": pannelli_per_fila,
        "num_file": num_file,
        "base_pannello": base_pannello,
        "altezza_pannello": altezza_pannello,
        "area": altezza_pannello * base_pannello,
        "pitch_laterale": pitch_laterale,
        "pitch_verticale": pitch_verticale,
        "altezza_suolo": altezza_suolo,
        "tilt_pannello": tilt,
        "azimuth_pannello": azimuth,
        "eff": eff,
        "temp_coeff": temp_coeff,
        "noct": noct,
    }


# ==================== SISTEMA ELETTRICO ====================
def get_electrical_parameters():
    with st.sidebar.expander("⚡ Sistema elettrico", expanded=False):
        col1, col2 = st.columns(2)
        losses = col1.number_input("Perdite sistema [%]", value=DEFAULT_PARAMS["losses"]*100, step=1.0, min_value=0.0, max_value=50.0)/100
        albedo = col2.number_input("Albedo", value=DEFAULT_PARAMS["albedo"], step=0.05, min_value=0.0, max_value=1.0, format="%.2f")
    return {"losses": losses, "albedo": albedo}

# ==================== PARAMETRI AGGIUNTIVI ====================
def get_additional_parameters():
    with st.sidebar.expander("🧩 Parametri aggiuntivi", expanded=False):
        col1, col2 = st.columns(2)
        extra_param1 = col1.number_input("Parametro extra 1", value=0.0, step=0.1)
        extra_param2 = col2.number_input("Parametro extra 2", value=0.0, step=0.1)
    return {"extra_param1": extra_param1, "extra_param2": extra_param2}

# ==================== VALIDAZIONE ====================
def validate_and_display_status(panel_params):
    superficie_effettiva, gcr = calculate_coverage(panel_params["num_panels"], panel_params["area"])
    is_valid = superficie_effettiva <= HECTARE_M2
    if not is_valid:
        max_panels = int(HECTARE_M2 // panel_params["area"])
        st.sidebar.warning(f"⚠️ Superficie totale ({superficie_effettiva:.0f} m²) supera 1 ettaro! Max pannelli: {max_panels}")
    else:
        st.sidebar.success(f"Superficie valida: {superficie_effettiva:.0f} m², GCR: {gcr:.2f}")
    return {"is_surface_valid": is_valid, "superficie_effettiva": superficie_effettiva, "gcr": gcr}

# ==================== FUNZIONE PRINCIPALE ====================
def sidebar_inputs():
    display_sidebar_header()
    location_data = get_location_and_date_inputs()
    panel_params = get_panel_geometry()
    electrical_params = get_electrical_parameters()
    additional_params = get_additional_parameters()
    validation_results = validate_and_display_status(panel_params)
    return {**location_data, **panel_params, **electrical_params, **additional_params, **validation_results}
