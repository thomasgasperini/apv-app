import streamlit as st

# ==================== CONTENUTI GUIDA ====================

def get_header_content() -> str:
    return """
    <div class="main-header">
        <h1>Analisi Produzione Fotovoltaico</h1>
        <p>Simulazione dei parametri solari e geometrici per impianti fotovoltaici</p>
    </div>
    """

def get_introduction_text() -> str:
    return """
    ## Guida ai Parametri Fotovoltaici
    
    Questa guida mostra i parametri di input, i calcoli PV e i principali output
    con codice e formule matematiche, chiarendo da dove derivano le variabili.
    """

def get_input_info() -> str:
    return """
    ### Parametri di INPUT (inseriti dall'utente)
    
    - Numero pannelli / ha  (`num_panels`)
    - Lato minore e maggiore pannello [m]  (`base`, `altezza_pannello`)
    - Altezza dal suolo [m]  (`altezza`)
    - Tilt pannello [°]  (`tilt_pannello`)
    - Azimuth pannello [°]  (`azimuth_pannello`)
    - Efficienza [%]  (`eff`)
    - Coefficiente temperatura [%/°C]  (`temp_coeff`)
    - NOCT [°C]  (`noct`)
    - Perdite sistema [%]  (`losses`)
    - Albedo [0-1]  (`albedo`)
    - Data simulazione  (`data`)
    - Localizzazione  (`lat`, `lon`)
    """

# ==================== FUNZIONE PRINCIPALE GUIDA ====================

def show_pv_guide():
    """
    Visualizza guida completa con spiegazioni dei parametri input/output
    e codice corrispondente a calcoli reali con pvlib.
    """
    with st.expander("Guida completa Fotovoltaico", expanded=True):
        # Header
        st.markdown(get_header_content(), unsafe_allow_html=True)
        
        # Introduzione
        st.markdown(get_introduction_text())
        
        # Parametri di input
        st.markdown(get_input_info())
        st.markdown("---")

        # ==================== OUTPUT ====================

        st.markdown("### Parametri di OUTPUT (con codice e formule)")

        # --- Superficie Totale Pannelli ---
        st.markdown("**Superficie Totale Pannelli [m²]**")
        st.markdown("Area totale occupata dai pannelli: numero pannelli × area singolo pannello")
        st.code("""
# num_panels, base, altezza_pannello = input utente
panel_area = base * altezza_pannello  # calcolo area singolo pannello
""", language="python")
        st.latex(r"A_{totale} = N_{pannelli} \times A_{pannello}")

        # --- Land Area Coverage (GCR) ---
        st.markdown("**Land Area Coverage (GCR) [%]**")
        st.markdown("Percentuale della superficie del terreno effettivamente coperta dai pannelli")
        st.code("""
# HECTARE_M2 = 10000 m² (1 ettaro)
superficie_effettiva, gcr = calculate_coverage(num_panels, panel_area)
gcr = superficie_effettiva / HECTARE_M2
""", language="python")
        st.latex(r"GCR = \frac{A_{totale}}{A_{terreno}}")

        # --- Posizione solare e irradianza clearsky ---
        st.markdown("**GHI, DNI, DHI [W/m²]**")
        st.markdown("I valori orari derivano dal modello cielo sereno (pvlib), usando lat/lon e data")
        st.code("""
import pvlib
import pandas as pd

# Timeline oraria della giornata
times = pd.date_range(start=data, end=data + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
                      freq="1h", tz=timezone)

# Posizione solare
solpos = pvlib.solarposition.get_solarposition(times, lat, lon)

# Irradianza in cielo sereno (clearsky)
site = pvlib.location.Location(lat, lon, tz=timezone)
clearsky = site.get_clearsky(times, model="ineichen")

# Valori orari
df_ghi = clearsky['ghi']   # Global Horizontal Irradiance [W/m²]
df_dni = clearsky['dni']   # Direct Normal Irradiance [W/m²]
df_dhi = clearsky['dhi']   # Diffuse Horizontal Irradiance [W/m²]

# Valori medi giornalieri
GHI_medio = df_ghi.mean()
DNI_medio = df_dni.mean()
DHI_medio = df_dhi.mean()
""", language="python")
        st.latex(r"\text{GHI}_{medio} = \frac{\sum \text{GHI}}{n}")
        st.latex(r"\text{DNI}_{medio} = \frac{\sum \text{DNI}}{n}")

        # --- POA Medio ---
        st.markdown("**POA (Plane of Array) [W/m²]**")
        st.markdown("I valori derivano dai dati GHI, DNI, DHI e dai parametri tilt, azimuth, albedo")
        st.code("""
# POA = Irradianza sul piano del modulo
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt_pannello,
    surface_azimuth=azimuth_pannello,
    dni=clearsky['dni'],
    ghi=clearsky['ghi'],
    dhi=clearsky['dhi'],
    solar_zenith=solpos['zenith'],
    solar_azimuth=solpos['azimuth'],
    albedo=albedo
)

POA_medio = poa['poa_global'].mean()
""", language="python")
        st.latex(r"POA = DNI \cdot \cos(\theta_i) + DHI + GHI \cdot \text{albedo}")

        # Note finali
        st.markdown("---")
        st.markdown("""
**Note:**
- La simulazione utilizza il modello Ineichen per il cielo sereno
- Tutti i valori di irradiance oraria (GHI, DNI, DHI, POA) provengono dalla libreria pvlib
- I valori medi giornalieri sono calcolati come media aritmetica dei valori orari
- GCR e superficie derivano dai parametri geometrici dei pannelli inseriti dall'utente
        """)

        # Bibliografia
        st.markdown("---")
        st.markdown("### Bibliografia e Riferimenti")
        st.markdown("""
1. Duffie, J.A., Beckman, W.A. *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013.
2. PVLib Python Documentation – https://pvlib-python.readthedocs.io/
3. Ineichen, P. *A broadband simplified version of the Solis clear sky model*, Solar Energy, 2008.
4. IEA PVPS, *Trends in Photovoltaic Applications*, International Energy Agency, annual report.
5. Perez, R., Seals, R., Ineichen, P., *Modeling Daylight Availability and Irradiance Components from Direct and Global Irradiance*, Solar Energy, 1990.
        """)
