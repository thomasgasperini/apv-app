# sidebar.py
from datetime import date
import streamlit as st
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from config import DEFAULT_PARAMS, LOGO_URL, TIMEZONE
from calculations import validate_surface, HECTARE_M2


def display_sidebar_header():
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


def get_location_inputs():
    with st.sidebar.expander("📍 Localizzazione", expanded=False):
        comune = st.text_input("Comune", value=DEFAULT_PARAMS["comune"])
        geolocator = Nominatim(user_agent="pv_calculator_pro")
        location = geolocator.geocode(f"{comune}, Italia", timeout=10)
        if location:
            lat, lon = location.latitude, location.longitude
        else:
            lat = st.number_input("Lat [°]", value=DEFAULT_PARAMS["lat"], format="%.2f")
            lon = st.number_input("Lon [°]", value=DEFAULT_PARAMS["lon"], format="%.2f")
            location = None
        timezone = ZoneInfo(TIMEZONE)
    return comune, lat, lon, timezone, location


def get_date_input():
    with st.sidebar.expander("📅 Data simulazione", expanded=False):
        data = st.date_input("Seleziona data", value=date.today())
    return data


def get_panel_parameters():
    with st.sidebar.expander("🔧 Parametri pannello", expanded=False):
        col1, col2 = st.columns(2)

        # --- COLONNA 1 ---
        with col1:
            num_panels = st.number_input("Numero pannelli / ha", value=DEFAULT_PARAMS["num_panels"], step=1, min_value=1)
            base = st.number_input("Lato minore pannello [m]", value=1.0, step=0.1, min_value=0.1)
            altezza_pannello = st.number_input("Lato maggiore pannello [m]", value=1.0, step=0.1, min_value=0.1)
            area = base * altezza_pannello  # Calcolo area

            st.markdown(f"""
                <div style="margin-bottom:0.6rem;">
                    <label style="font-weight:600;font-size:0.9rem;color:var(--text-color);display:block;margin-bottom:0.2rem;">
                        Area pannello [m²]
                    </label>
                    <input type="text" value="{area:.2f}" readonly
                        style="background-color:var(--background-color);
                            color:var(--text-color);
                            border:1px solid var(--border-color);
                            border-radius:0.5rem;
                            padding:0.4rem 0.5rem;
                            width:100%;
                            font-size:0.9rem;
                            font-family:inherit;
                            cursor:default;">
                </div>
            """, unsafe_allow_html=True)

            altezza = st.number_input("Altezza dal suolo dei pannelli [m]", value=DEFAULT_PARAMS["altezza"], step=0.1)
            pitch_laterale = st.number_input("Pitch laterale [m]", value=DEFAULT_PARAMS["pitch_laterale"], step=0.05)
            pitch_file = st.number_input("Pitch tra file [m]", value=DEFAULT_PARAMS["pitch_file"], step=0.05)

        # --- COLONNA 2 ---
        with col2:
            tilt_pannello = st.slider("Tilt pannello [°]", 0, 90, DEFAULT_PARAMS["tilt"])
            azimuth_pannello = st.slider("Azimuth pannello [°]", -180, 180, DEFAULT_PARAMS["azimuth"])
            temp_coeff = st.number_input("γ [%/°C]", value=DEFAULT_PARAMS["temp_coeff"]*100, step=0.1)/100
            eff = st.number_input("Efficienza [%]", value=DEFAULT_PARAMS["eff"]*100, step=0.5)/100
            noct = st.number_input("NOCT [°C]", value=DEFAULT_PARAMS["noct"])

    return {
        "num_panels": num_panels,
        "base": base,
        "altezza_pannello": altezza_pannello,
        "area": area,
        "altezza": altezza,
        "pitch_laterale": pitch_laterale,
        "pitch_file": pitch_file,
        "tilt_pannello": tilt_pannello,
        "azimuth_pannello": azimuth_pannello,
        "temp_coeff": temp_coeff,
        "eff": eff,
        "noct": noct,
    }



def get_electrical_parameters():
    with st.sidebar.expander("⚡ Sistema elettrico", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            losses = st.number_input("Perdite [%]", value=DEFAULT_PARAMS["losses"]*100, step=1.0)/100
        with col2:
            albedo = st.number_input("Albedo", value=DEFAULT_PARAMS["albedo"], step=0.05)
    return losses, albedo


def get_additional_parameters():
    with st.sidebar.expander("🧩 Parametri aggiuntivi", expanded=False):
        extra_param = st.number_input("Param extra", value=0.0)
    return extra_param


def sidebar_inputs():
    display_sidebar_header()
    comune, lat, lon, timezone, location = get_location_inputs()
    data = get_date_input()
    panel_params = get_panel_parameters()

    num_panels = panel_params["num_panels"]
    area = panel_params["area"]
    pitch_laterale = panel_params["pitch_laterale"]
    pitch_file = panel_params["pitch_file"]

    # --- Validazione superficie ---
    is_valid, fattore_copertura_max, superficie_effettiva, gcr = validate_surface(
        num_panels, area
    )

    if not is_valid:
        st.sidebar.warning(
            f"⚠️ Attenzione: la superficie totale ({superficie_effettiva:.0f} m²) "
            f"supera 1 ettaro ({HECTARE_M2} m²)! "
            f"Numero massimo pannelli consentito: "
            f"{int(HECTARE_M2 // (pitch_laterale * pitch_file))}."
        )
    else:
        st.sidebar.success(f"✅ Input validi (pannelli/ha): {superficie_effettiva:.0f} m² ({gcr:.2%} Ground Coverage Ratio)")

    losses, albedo = get_electrical_parameters()
    extra_param = get_additional_parameters()

    return {
        "comune": comune,
        "lat": lat,
        "lon": lon,
        "timezone": timezone,
        "data": data,
        "area": area,
        "location": location,
        "losses": losses,
        "albedo": albedo,
        "extra_param": extra_param,
        **panel_params,
        "is_surface_valid": is_valid,
        "fattore_copertura_max": fattore_copertura_max,
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr,
    }
