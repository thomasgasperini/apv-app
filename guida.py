import streamlit as st

# ==================== CONTENUTI GUIDA ====================

def get_header_content() -> str:
    return r"""
    <div style="text-align:center; margin-top:-10px; margin-bottom:20px;">
        <h1 style="color:#1F618D; font-weight:700;"> Guida Avanzata al Simulatore APV di RESFARM</h1>
        <p style="font-size:16px; color:#555; line-height:1.5;">
            Simulazione completa dei parametri solari, geometrici e di produzione per impianti APV.
        </p>
    </div>
    """

def get_introduction_text() -> str:
    return r"""
    ## Introduzione alla Simulazione Fotovoltaica
    
    Questa guida illustra i passaggi fondamentali per stimare la produzione di un impianto fotovoltaico, 
    partendo dai **parametri geometrici e ambientali**, passando per i **modelli di irraggiamento solare**, 
    fino alla **stima della produzione elettrica giornaliera**.
    
    Verranno presentati sia i **concetti teorici** che la **loro implementazione in Python**, sfruttando 
    la libreria `pvlib`.
    """

def get_input_info() -> str:
    return r"""
    ### Parametri di Input
    
    I principali dati richiesti per la simulazione sono:
    
    - **Numero pannelli per ha** (`num_panels`)
    - **Dimensioni pannello [m]**: base (`base`), altezza (`altezza_pannello`)
    - **Altezza dal suolo [m]** (`altezza`)
    - **Tilt e azimuth pannello [°]** (`tilt_pannello`, `azimuth_pannello`)
    - **Efficienza modulo [%]** (`eff`)
    - **Coefficiente di temperatura [%/°C]** (`temp_coeff`)
    - **NOCT [°C]** (`noct`)
    - **Perdite di sistema [%]** (`losses`)
    - **Albedo del terreno [0–1]** (`albedo`)
    - **Data simulazione** (`data`)
    - **Coordinate geografiche** (`lat`, `lon`)
    """

# ==================== FUNZIONE PRINCIPALE ====================

def show_pv_guide():
    with st.expander("📖 Guida Completa", expanded=False):
        

        # Header
        st.markdown(get_header_content(), unsafe_allow_html=True)
        st.markdown(get_introduction_text())

        # ==================== INPUT ====================
        st.markdown(get_input_info())
        st.markdown("---")

        # ==================== CALCOLI GEOMETRICI ====================
        st.markdown("## 1. Calcoli Geometrici")
        
        # --- Superficie totale pannelli ---
        st.markdown("### 1.1 Superficie Totale Pannelli [m²]")
        st.markdown("L'**area totale dei pannelli** si calcola con le seguenti formule:")
        st.latex(r"""
        A_{\text{pannello}} = \text{base} \times \text{altezza} \\
        A_{\text{totale}} = N_{\text{pannelli}} \times A_{\text{pannello}}
        """)
        st.code("""panel_area = base * altezza_pannello
superficie_totale = num_panels * panel_area""", language="python")

        # --- Land Area Coverage (GCR) ---
        st.markdown("### 1.2 Land Area Coverage (GCR) [%]")
        st.markdown("Il **GCR** rappresenta la frazione di terreno coperta dai pannelli:")
        st.latex(r"""
        GCR = \frac{A_{\text{totale}}}{A_{\text{terreno}}}, \quad
        A_{\text{terreno}} = 10.000\,\text{m² per ha}
        """)
        st.code("""superficie_effettiva, gcr = calculate_coverage(num_panels, panel_area)
gcr = superficie_effettiva / HECTARE_M2""", language="python")
        st.markdown("---")

        # ==================== CALCOLI SOLARI ====================
        st.markdown("## 2. Calcoli Solari (Irradianza)")

        # --- GHI ---
        st.markdown("### 2.1 GHI – Global Horizontal Irradiance [W/m²]")
        st.markdown("La GHI rappresenta la **radiazione totale su un piano orizzontale**:")
        st.latex(r"\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}")

        # --- DNI ---
        st.markdown("### 2.2 DNI – Direct Normal Irradiance [W/m²]")
        st.markdown("Radiazione solare diretta misurata perpendicolarmente ai raggi solari:")
        st.latex(r"\text{DNI} = \frac{\text{GHI} - \text{DHI}}{\cos(\theta_z)}")

        # --- DHI ---
        st.markdown("### 2.3 DHI – Diffuse Horizontal Irradiance [W/m²]")
        st.markdown("Componente diffusa della radiazione proveniente da tutto il cielo eccetto il sole:")
        st.latex(r"\text{DHI} = \text{GHI} - \text{DNI} \cdot \cos(\theta_z)")

        # --- POA ---
        st.markdown("### 2.4 POA – Plane of Array Irradiance [W/m²]")
        st.markdown("Radiazione incidente sul piano inclinato del modulo:")
        st.latex(r"""
        \text{POA} = \text{DNI} \cdot \cos(\theta_i) + \text{DHI} + \text{GHI} \cdot \text{albedo} \\
        \theta_i = \text{angolo di incidenza sul pannello}
        """)

        st.markdown("---")

        # ==================== IMPLEMENTAZIONE CODICE ====================
        st.markdown("## 3. Implementazione Python con `pvlib`")
        st.markdown("Passaggi principali:")
        st.markdown("""
        1. Creazione della timeline oraria
        2. Calcolo posizione solare (`pvlib.solarposition`)
        3. Stima radiazione cielo sereno (Ineichen)
        4. Calcolo radiazione sul piano moduli (POA)
        """)
        st.code("""import pvlib
import pandas as pd

times = pd.date_range(start=data,
                      end=data + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
                      freq='1h', tz=timezone)

site = pvlib.location.Location(lat, lon, tz=timezone)
solpos = pvlib.solarposition.get_solarposition(times, lat, lon)
clearsky = site.get_clearsky(times, model='ineichen')

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

POA_medio = poa['poa_global'].mean()""", language="python")

        st.markdown("---")

        # ==================== PRODUZIONE ELETTRICA ====================
        st.markdown("## 4. Calcolo Produzione Elettrica")
        st.markdown("La potenza istantanea del modulo si calcola come:")
        st.latex(r"""
        P_{\text{inst}} = POA \cdot A_{\text{totale}} \cdot \eta_{\text{corr}} \cdot (1 - \text{losses}) \\
        \eta_{\text{corr}} = \eta \cdot \left[1 + \text{temp\_coeff} \cdot (T_{\text{cell}} - 25)\right] \\
        T_{\text{cell}} = 25 + \frac{POA}{800} \cdot (NOCT - 20)
        """)
        st.code("""T_cell = 25 + (poa_global / 800) * (noct - 20)
eff_corr = eff * (1 + temp_coeff * (T_cell - 25))
P_inst = poa_global * area * num_panels * eff_corr * (1 - losses)
E_day = P_inst.sum()""", language="python")

        st.markdown("---")

        # ==================== NOTE FINALI ====================
        st.markdown("## 5. Note Finali")
        st.markdown("""
        - Tutti i valori di irradiamento (GHI, DNI, DHI, POA) sono riferiti a **1 m²**.
        - I valori giornalieri si ottengono **sommando o mediando** quelli orari.
        - Il modello di cielo sereno utilizzato è **Ineichen** (`pvlib`).
        - La superficie e il GCR derivano esclusivamente dai parametri geometrici dei pannelli.
        """)

        # ==================== BIBLIOGRAFIA ====================
        st.markdown("## Bibliografia e Riferimenti")
        st.markdown("""
        1. Duffie, J.A., Beckman, W.A., *Solar Engineering of Thermal Processes*, 4th Ed., Wiley, 2013.
        2. PVLib Python Documentation – [https://pvlib-python.readthedocs.io](https://pvlib-python.readthedocs.io)
        3. Ineichen, P., *A broadband simplified version of the Solis clear sky model*, Solar Energy, 2008.
        4. Perez, R., Seals, R., Ineichen, P., *Modeling Daylight Availability and Irradiance Components*, Solar Energy, 1990.
        5. IEA PVPS, *Trends in Photovoltaic Applications*, International Energy Agency.
        """)
