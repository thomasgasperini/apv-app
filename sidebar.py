"""
Modulo Sidebar - Raccolta input utente
Gestisce tutti i parametri di input in modo pulito e organizzato
"""

from shapely import area
import streamlit as st
from datetime import date
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
import time
from config import DEFAULT_PARAMS, LOGO_URL, TIMEZONE_OBJ


# ==================== HEADER SIDEBAR ====================

def display_sidebar_header():
    """Visualizza logo e titolo nella sidebar in modo responsive"""
    st.sidebar.markdown(f"""
    <style>
        section[data-testid="stSidebar"] button[kind="icon"],
        section[data-testid="stSidebar"] [role="button"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {{
            position: relative !important;
            top: -1rem !important;
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
            padding: 0.5vw; /* padding scalabile */
            margin-top: -10vh;
            margin-bottom: -1vh;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        
        .sidebar-header-logo img {{
            width: auto;
            height: auto;
            max-height: 20vh; /* scala con altezza viewport */
            max-width: 90%;   /* scala con larghezza contenitore */
            object-fit: contain;
            object-position: center;
            border-radius: 5px;
        }}
        
        @media (max-width: 600px) {{
            .sidebar-header-logo {{
                padding: 4vw;
            }}
            .sidebar-header-logo img {{
                max-height: 20vh;
            }}
        }}
    </style>
    
    <div class="sidebar-header-logo">
        <img src="{LOGO_URL}" alt="Logo">
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(
        "<h3 style='text-align:center; margin-bottom:0rem;'>Interfaccia INPUT</h3>", 
        unsafe_allow_html=True
    )


from functools import lru_cache

@lru_cache(maxsize=200)
def cached_geocode(comune: str):
    geolocator = Nominatim(user_agent="resfarm@monitoring.com", timeout=10)
    return geolocator.geocode(f"{comune}, Italia")


def get_location_from_comune(comune: str, max_retries: int = 3):
    """Ritorna (lat, lon, location) o (None, None, None) se fallisce"""
    for attempt in range(max_retries):
        try:
            if loc := cached_geocode(comune):
                return loc.latitude, loc.longitude, loc
        except (GeocoderServiceError, GeocoderTimedOut):
            time.sleep(attempt + 1)
        except Exception:
            break

    return None, None, None

# ==================== SEZIONI INPUT ====================

def get_location_and_date():
    """Raccoglie località e data simulazione"""
    with st.sidebar.expander("🌍 Localizzazione e Data", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            comune = st.text_input("Comune", value=DEFAULT_PARAMS["comune"])
            lat, lon, location = get_location_from_comune(comune)
        
        with col2:
            data_sim = st.date_input("Data", value=date.today())
        
        # Fallback manuale se geocoding fallisce
        if lat is None or lon is None:
            lat = st.number_input("Latitudine [°]", value=DEFAULT_PARAMS["lat"], format="%.4f")
            lon = st.number_input("Longitudine [°]", value=DEFAULT_PARAMS["lon"], format="%.4f")
            location = None
    
    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": TIMEZONE_OBJ,
        "location": location,
        "data": data_sim
    }


def get_all_panel_params():
    """Raccoglie tutti i parametri dei pannelli in un unico expander"""
    
    with st.sidebar.expander("⚙️ Parametri Pannelli", expanded=False):
        
        # --- Layout Pannelli ---
        col1, col2 = st.columns(2)

        num_per_row = col1.number_input(
            "Pannelli per Fila",
            value=int(DEFAULT_PARAMS["num_panels_per_row"]),
            min_value=1,
            step=1,
            help="Numero pannelli in ogni fila"
        )
        num_rows = col2.number_input(
            "Numero File",
            value=int(DEFAULT_PARAMS["num_rows"]),
            min_value=1,
            step=1,
            help="Numero di file di pannelli"
        )

        num_panels_total = num_per_row * num_rows
        
        # Totale pannelli + Altezza dal suolo
        col1, col2 = st.columns(2)
        col1.text_input(
            "Totale Pannelli",
            value=str(num_panels_total),
            disabled=True,
            help="Numero totale pannelli installati"
        )
        
        # Altezza sostituisce Ettari
        altezza_suolo = col2.number_input(
            "Altezza dal Suolo [m]",
            value=float(DEFAULT_PARAMS.get("altezza_suolo", 1.0)),
            min_value=0.1,
            max_value=10.0,
            step=0.1,
            help="Distanza tra la base del pannello e il terreno"
        )

        # --- Dimensioni moduli ---
        col1, col2 = st.columns(2)

        lato_maggiore = col1.number_input(
            "Lato Maggiore [m]",
            value=float(DEFAULT_PARAMS["lato_maggiore"]),
            min_value=0.1,
            step=0.1,
            help="Lato lungo del pannello"
        )
        lato_minore = col2.number_input(
            "Lato Minore [m]",
            value=float(DEFAULT_PARAMS["lato_minore"]),
            min_value=0.1,
            step=0.1,
            help="Lato corto del pannello"
        )

        area = lato_maggiore * lato_minore

        st.text_input(
            "Area Pannello [m²]",
            value=f"{area:.2f}",
            disabled=True,
            help="Superficie di un pannello"
        )

        # --- Spaziatura ---
        col1, col2 = st.columns(2)

        carreggiata = col1.number_input(
            "Carreggiata [m]",
            value=float(DEFAULT_PARAMS["carreggiata"]),
            min_value=0.0,
            step=0.5,
            help="Distanza tra file"
        )
        pitch = col2.number_input(
            "Pitch Laterale [m]",
            value=float(DEFAULT_PARAMS["pitch_laterale"]),
            min_value=0.0,
            step=0.1,
            help="Distanza tra centri di pannelli"
        )

        # --- Orientamento ---
        col1, col2 = st.columns(2)

        tilt = col1.slider(
            "Tilt [°]",
            0, 90,
            int(DEFAULT_PARAMS["tilt"]),
            help="Inclinazione rispetto all'orizzontale"
        )
        azimuth = col2.slider(
            "Azimuth [°]",
            0, 360,
            int(DEFAULT_PARAMS["azimuth"]),
            help="Direzione del pannello"
        )

        # --- Parametri elettrici ---
        col1, col2 = st.columns(2)

        eff = col1.number_input(
            "Efficienza [%]",
            value=float(DEFAULT_PARAMS["eff"] * 100),
            min_value=0.1,
            max_value=100.0,
            step=0.5,
            help="Rendimento del pannello fotovoltaico"
        ) / 100

        temp_coeff = col2.number_input(
            "Coeff. γ [%/°C]",
            value=float(DEFAULT_PARAMS["temp_coeff"] * 100),
            step=0.1,
            help="Perdita di potenza per aumento temperatura"
        ) / 100

        noct = st.number_input(
            "NOCT [°C]",
            value=float(DEFAULT_PARAMS["noct"]),
            min_value=20.0,
            max_value=60.0,
            step=1.0,
            help="Temperatura operativa tipica del pannello"
        )

    return {
        "num_panels_per_row": num_per_row,
        "num_rows": num_rows,
        "num_panels_total": num_panels_total,
        "lato_maggiore": lato_maggiore,
        "lato_minore": lato_minore,
        "area_pannello": area,
        "carreggiata": carreggiata,
        "pitch_laterale": pitch, 
        "altezza_suolo": altezza_suolo,  
        "tilt_pannello": tilt,
        "azimuth_pannello": azimuth,
        "eff": eff,
        "temp_coeff": temp_coeff,
        "noct": noct
    }


def get_system_params():
    """Raccoglie parametri sistema"""
    with st.sidebar.expander("⚡ Sistema Elettrico", expanded=False):
        col1, col2 = st.columns(2)
        
        losses = col1.number_input(
            "Perdite Sistema [%]",
            value=float(DEFAULT_PARAMS["losses"] * 100),
            min_value=0.0,
            max_value=50.0,
            step=1.0,
            help="Perdite totali"
        ) / 100
        
        albedo = col2.number_input(
            "Albedo",
            value=float(DEFAULT_PARAMS["albedo"]),
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            format="%.2f",
            help="Riflettività suolo"
        )
    
    return {
        "losses": losses,
        "albedo": albedo
    }

def get_agricultural_params():
    """Raccoglie parametri agricoli"""
    with st.sidebar.expander("🌽 Parametri Agricoli", expanded=False):
        col1, col2 = st.columns(2)
        hectares = col1.number_input(
            "Ettari Totali",
            value=float(DEFAULT_PARAMS["hectares"]),
            min_value=0.1,
            step=0.1,
            format="%.2f",
            help="Superficie disponibile del sito"
        )
        colture = col2.selectbox(
            "Tipo di Coltura",
            options=[
                "Microgreens",
                "Ortaggi a foglia",
                "Tuberi",
                "Ortaggi da frutto bassi",
                "Cereali",
                "Legumi",
                "Ortaggi da frutto alti",
                "Frutta (alberi e arbusti)",
                "Viti",
                "Piante ornamentali alte"
            ],
            index=0,
            help="Seleziona il tipo di coltura"
        )

    return {
        "crops": colture,
        "hectares": hectares
    }

# ==================== FUNZIONE PRINCIPALE ====================

def sidebar_inputs():
    """
    Funzione principale - raccoglie tutti gli input utente
    
    Returns:
        dict: Tutti i parametri raccolti
    """
    
    display_sidebar_header()
    
    # Raccolta input
    location_data = get_location_and_date()
    panel_params = get_all_panel_params()  
    system = get_system_params()
    crops = get_agricultural_params()

    # Merge tutti i parametri
    return {
        **location_data,
        **panel_params,
        **system,
        **crops
    }
