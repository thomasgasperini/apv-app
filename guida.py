import streamlit as st

# ==================== CONTENUTI GUIDA ====================

def get_header_content() -> str:
    return """
    <div style="text-align:center; margin-top:-20px; margin-bottom:10px;">
        <h1 style="color:#2E86C1;">Analisi Produzione Fotovoltaico</h1>
        <p style="font-size:17px; color:#555;">
            Simulazione dei parametri solari e geometrici per impianti fotovoltaici
        </p>
    </div>
    """

def get_introduction_text() -> str:
    return """
    ## Guida ai Parametri Fotovoltaici
    
    Questa guida mostra i parametri di input, i calcoli PV e i principali output,
    con codice e formule matematiche, chiarendo da dove derivano le variabili e il loro significato fisico.
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
    - Albedo [0–1]  (`albedo`)
    - Data simulazione  (`data`)
    - Localizzazione geografica  (`lat`, `lon`)
    """

# ==================== FUNZIONE PRINCIPALE ====================

def show_pv_guide():
    with st.expander("Guida completa Fotovoltaico", expanded=True):

        # Header
        st.markdown(get_header_content(), unsafe_allow_html=True)
        st.markdown(get_introduction_text())

        # ==================== INPUT ====================
        st.markdown(get_input_info())
        st.markdown("---")

        # ==================== OUTPUT ====================
        st.markdown("### Parametri di OUTPUT (con codice e formule)")

        # --- Superficie Totale Pannelli ---
        st.markdown("**Superficie Totale Pannelli [m²]**")
        st.markdown("Area totale occupata dai pannelli: numero pannelli × area singolo pannello.")
        st.code("""
# num_panels, base, altezza_pannello = input utente
panel_area = base * altezza_pannello
superficie_totale = num_panels * panel_area
""", language="python")
        st.latex(r"A_{totale} = N_{pannelli} \times A_{pannello}")

        # --- Land Area Coverage (GCR) ---
        st.markdown("**Land Area Coverage (GCR) [%]**")
        st.markdown("Percentuale della superficie del terreno effettivamente coperta dai pannelli.")
        st.code("""
# HECTARE_M2 = 10_000 m² (1 ettaro)
superficie_effettiva, gcr = calculate_coverage(num_panels, panel_area)
gcr = superficie_effettiva / HECTARE_M2
""", language="python")
        st.latex(r"GCR = \frac{A_{totale}}{A_{terreno}}")

        # --- GHI ---
        st.markdown("**GHI – Global Horizontal Irradiance [W/m²]**")
        st.markdown("""
È la **radiazione solare totale ricevuta su una superficie orizzontale**.  
Comprende due componenti:
- **Diretta (DNI)**: proveniente direttamente dal disco solare.  
- **Diffusa (DHI)**: dovuta alla dispersione atmosferica e alla riflessione delle nuvole.
""")
        st.latex(r"\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}")
        st.markdown("""
Dove:
- \\(\\theta_z\\) è l'angolo zenitale solare.
- La **GHI** rappresenta la quantità totale di energia solare disponibile su un piano orizzontale (ad esempio, il suolo).
""")

        # --- DNI ---
        st.markdown("**DNI – Direct Normal Irradiance [W/m²]**")
        st.markdown("""
È la **radiazione solare diretta per unità di superficie perpendicolare ai raggi solari**.  
Si misura su un piano normale alla direzione del Sole.
""")
        st.latex(r"\text{DNI} = \frac{\text{GHI} - \text{DHI}}{\cos(\theta_z)}")

        # --- DHI ---
        st.markdown("**DHI – Diffuse Horizontal Irradiance [W/m²]**")
        st.markdown("""
È la **radiazione solare diffusa che arriva da tutto il cielo**, eccetto il disco solare.  
Proviene dalla dispersione della luce nell’atmosfera ed è sempre presente, anche con cielo coperto.
""")
        st.latex(r"\text{DHI} = \text{GHI} - \text{DNI} \cdot \cos(\theta_z)")

        # --- POA ---
        st.markdown("**POA – Plane of Array Irradiance [W/m²]**")
        st.markdown("""
È la **radiazione solare totale ricevuta sul piano del modulo fotovoltaico**, inclinato e orientato secondo tilt e azimuth.
Comprende tre contributi:
- Diretto proiettato sul piano del modulo  
- Diffuso del cielo  
- Riflesso dal suolo (in funzione dell’albedo)
""")
        st.latex(r"\text{POA} = \text{DNI} \cdot \cos(\theta_i) + \text{DHI} + \text{GHI} \cdot \text{albedo}")
        st.markdown("""
Dove:
- \\(\\theta_i\\) è l’angolo di incidenza tra il raggio solare e la normale al pannello.  
- L’albedo rappresenta la frazione di luce riflessa dal suolo (es. 0.2 per terreno erboso, 0.8 per neve).
""")

        st.markdown("---")

        # ==================== IMPLEMENTAZIONE CODICE ====================
        st.markdown("### Implementazione dei calcoli con `pvlib`")

        st.code("""
import pvlib
import pandas as pd

# Timeline oraria della giornata
times = pd.date_range(
    start=data,
    end=data + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
    freq="1h",
    tz=timezone
)

# Posizione solare
solpos = pvlib.solarposition.get_solarposition(times, lat, lon)

# Irradianza in cielo sereno (modello Ineichen)
site = pvlib.location.Location(lat, lon, tz=timezone)
clearsky = site.get_clearsky(times, model="ineichen")

# Estrazione valori
df_ghi = clearsky['ghi']   # Global Horizontal Irradiance [W/m²]
df_dni = clearsky['dni']   # Direct Normal Irradiance [W/m²]
df_dhi = clearsky['dhi']   # Diffuse Horizontal Irradiance [W/m²]

# Irradianza sul piano del modulo (POA)
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt_pannello,
    surface_azimuth=azimuth_pannello,
    dni=df_dni,
    ghi=df_ghi,
    dhi=df_dhi,
    solar_zenith=solpos['zenith'],
    solar_azimuth=solpos['azimuth'],
    albedo=albedo
)

POA_medio = poa['poa_global'].mean()
""", language="python")

        st.markdown("""
Il calcolo **POA** combina automaticamente le tre componenti (diretta, diffusa e riflessa)
in funzione della geometria del pannello e delle condizioni solari.
""")

        st.markdown("---")

        # ==================== NOTE FINALI ====================
        st.markdown("### Note importanti")
        st.markdown("""
- La simulazione utilizza il modello *Ineichen* per il cielo sereno, implementato in `pvlib`.  
- Tutti i valori (GHI, DNI, DHI, POA) sono riferiti a 1 m² di superficie.  
- I valori giornalieri si ottengono sommando o mediando quelli orari.  
- GCR e superficie derivano esclusivamente dai parametri geometrici dei pannelli.
""")

        # ==================== BIBLIOGRAFIA ====================
        st.markdown("### Bibliografia e Riferimenti")
        st.markdown("""
1. Duffie, J.A., Beckman, W.A. *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013.  
2. PVLib Python Documentation – [https://pvlib-python.readthedocs.io](https://pvlib-python.readthedocs.io)  
3. Ineichen, P. *A broadband simplified version of the Solis clear sky model*, Solar Energy, 2008.  
4. Perez, R., Seals, R., Ineichen, P., *Modeling Daylight Availability and Irradiance Components from Direct and Global Irradiance*, Solar Energy, 1990.  
5. IEA PVPS, *Trends in Photovoltaic Applications*, International Energy Agency.
""")
