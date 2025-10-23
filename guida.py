import streamlit as st
import pandas as pd

def show_pv_guide():
    """
    Mostra un rapporto tecnico completo sui calcoli fotovoltaici
    """
    # Stato del pulsante
    if 'show_guide' not in st.session_state:
        st.session_state.show_guide = False

    if st.button("📋 Mostra Rapporto Tecnico"):
        st.session_state.show_guide = not st.session_state.show_guide

    if not st.session_state.show_guide:
        return

    # Titolo e introduzione
    st.markdown("""
    # Rapporto Tecnico: Metodologia di Calcolo Fotovoltaico e Agro-FV

    **Documentazione completa degli algoritmi implementati per la simulazione 
    di impianti fotovoltaici in configurazione agro-fotovoltaica.**
    """)

    st.markdown("---")

    # 1. SCOPO E AMBITO
    st.markdown("""
    ## 1. Scopo e Ambito

    Questo documento descrive la metodologia di calcolo implementata per la stima della produzione energetica 
    di impianti fotovoltaici e della radiazione solare residua disponibile per coltivazioni (Agro-FV).
    
    **Ambito di applicazione**: Simulazioni giornaliere in condizioni di cielo sereno per configurazioni 
    fisse di pannelli fotovoltaici.
    """)

    st.markdown("---")

    # 2. PARAMETRI DI INPUT
    st.markdown("""
    ## 2. Parametri di Input

    I seguenti parametri sono richiesti per l'esecuzione dei calcoli:
    """)

    st.markdown("""
    ### 2.1 Parametri Geografici e Temporali
    ```python
    {
        "comune": ...,                      # Localizzazione per geocoding
        "lat": ..., "lon": ...,             # Coordinate geografiche [gradi decimali]
        "data": ...,                        # Data di simulazione [YYYY-MM-DD]
        "timezone": "Europe/Rome"           # Fuso orario
    }
    ```
    """)

    st.markdown("""
    ### 2.2 Parametri dei Pannelli e Configurazione
    ```python
    {
        "num_panels": ...,                  # Numero di pannelli per ettaro
        "Lato minore pannello": ...,        # Lato minore del pannello [m]
        "Lato maggiore pannello": ...,      # Lato maggiore del pannello [m]
        "tilt_pannello": ...,               # Inclinazione pannelli [gradi]
        "azimuth_pannello": ...,            # Orientamento (0=Nord, 180=Sud) [gradi]
        "eff": ...,                         # Efficienza di conversione [0-1]
        "temp_coeff": ...,                  # Coefficiente di temperatura [1/°C]
        "noct": ...,                        # Nominal Operating Cell Temperature [°C]
        "pitch_file": ...,                  # Distanza tra file di pannelli [m]
        "pitch_laterale": ...               # Distanza laterale tra pannelli [m]
    }
    ```
    """)

    st.markdown("""
    ### 2.3 Parametri di Sistema
    ```python
    {
        "losses": ...,                      # Perdite del sistema [0-1]
        "albedo": ...,                      # Riflettività del terreno [0-1]
        "T_ambiente": ...                   # Temperatura ambiente di riferimento [°C]
    }
    ```
    """)

    st.markdown("---")

    # 3. METODOLOGIA DI CALCOLO
    st.markdown("""
    ## 3. Metodologia di Calcolo

    Il flusso di calcolo segue una sequenza deterministica dove l'output di ogni fase 
    costituisce l'input per la fase successiva.
    """)

    st.markdown("""
    ### 3.1 Generazione Timeline e Posizione Solare

    **Implementazione**:
    ```python
    # Generazione serie temporale oraria per il giorno specificato
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # Calcolo posizione solare
    solpos = pvlib.solarposition.get_solarposition(times, params["lat"], params["lon"])
    # Output: zenith, azimuth, elevation angle per ogni intervallo temporale
    ```

    **Fondamento teorico**: Gli algoritmi di posizione solare si basano sulle equazioni 
    astronomiche standard (Reda & Andreas, 2004) per determinare con precisione la posizione 
    del sole in coordinate celesti.
    """)

    st.markdown("""
    ### 3.2 Radiazione in Cielo Sereno

    **Implementazione**:
    ```python
    site = pvlib.location.Location(params["lat"], params["lon"], tz=params["timezone"])
    clearsky = site.get_clearsky(times, model="ineichen")
    # Output: ghi, dni, dhi in W/m² per ogni intervallo orario
    ```

    **Modello Ineichen**: Questo modello stima la radiazione solare in condizioni di 
    cielo sereno considerando:
    - Trasparenza atmosferica (Linke turbidity)
    - Angolo di elevazione solare
    - Altitudine del sito

    **Componenti della radiazione**:
    - **GHI (Global Horizontal Irradiance)**: Radiazione totale su superficie orizzontale
    - **DNI (Direct Normal Irradiance)**: Radiazione diretta perpendicolare ai raggi solari  
    - **DHI (Diffuse Horizontal Irradiance)**: Radiazione diffusa dall'atmosfera
    """)

    st.markdown("""
    ### 3.3 Radiazione sul Piano dei Pannelli (POA)

    **Implementazione**:
    ```python
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=params["tilt_pannello"],
        surface_azimuth=params["azimuth_pannello"], 
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth'],
        albedo=params["albedo"]
    )
    # Output: poa_global, poa_direct, poa_diffuse, poa_sky_diffuse, poa_ground_diffuse
    ```

    **Modello di decomposizione**: La radiazione sul piano inclinato è calcolata come 
    somma di tre componenti:

    """)
    
    st.latex(r"""
    G_{POA} = G_{POA,diretta} + G_{POA,diffusa} + G_{POA,riflessa}
    """)
    
    st.latex(r"""
    \begin{align*}
    G_{POA,diretta} &= DNI \cdot \cos(\theta_i) \\
    G_{POA,diffusa} &= DHI \cdot \frac{1 + \cos(\beta)}{2} \\
    G_{POA,riflessa} &= GHI \cdot \rho \cdot \frac{1 - \cos(\beta)}{2}
    \end{align*}
    """)
    
    st.markdown("""
    dove:
    - $\\theta_i$: angolo di incidenza tra i raggi solari e la normale al piano del pannello
    - $\\beta$: angolo di tilt del pannello
    - $\\rho$: coefficiente di albedo del terreno
    """)

    st.markdown("""
    ### 3.4 Temperatura delle Celle Fotovoltaiche

    **Implementazione**:
    ```python
    def calculate_cell_temperature(poa_global, noct, ambient_temp=25):
        return ambient_temp + (noct - 20) / 800 * poa_global
    ```

    **Fondamento teorico**: Modello semplificato basato sulla definizione di NOCT 
    (Nominal Operating Cell Temperature) secondo lo standard IEC 60904-5:

    """)
    
    st.latex(r"""
    T_{cell} = T_{amb} + \frac{G_{POA}}{800} \cdot (NOCT - 20)
    """)
    
    st.markdown("""
    Il fattore 800 deriva dalle condizioni standard di misura del NOCT:
    - Irradianza: 800 W/m²
    - Temperatura ambiente: 20°C
    - Velocità del vento: 1 m/s
    - Montaggio: struttura aperta
    """)

    st.markdown("""
    ### 3.5 Produzione di Energia Elettrica

    **Potenza DC**:
    ```python
    def calculate_dc_power(poa_global, area, eff, T_cell, temp_coeff, T_ref=25):
        return (poa_global * area * eff * 
                (1 + temp_coeff * (T_cell - T_ref))) / 1000  # Conversione in kW
    ```

    **Equazione fondamentale**:
    """)
    
    st.latex(r"""
    P_{DC} = G_{POA} \cdot A \cdot \eta \cdot [1 + \gamma \cdot (T_{cell} - T_{ref})]
    """)
    
    st.markdown("""
    dove:
    - $A$: area del pannello [m²]
    - $\\eta$: efficienza di conversione del pannello
    - $\\gamma$: coefficiente di temperatura [1/°C]
    - $T_{ref}$: temperatura di riferimento (25°C)

    **Potenza AC**:
    ```python
    def calculate_ac_power(P_dc, losses):
        return P_dc * (1 - losses)  # P_dc in kW, output in kW
    ```

    **Energia giornaliera per ettaro**:
    ```python
    E_day = P_ac.sum() * fattore_copertura_max  # kWh/ha
    ```
    """)

    st.markdown("""
    ### 3.6 Radiazione al Suolo per Applicazioni Agro-FV

    **Implementazione migliorata**:
    ```python
    def calculate_ground_radiation_improved(clearsky_ghi, solpos, panel_area, 
                                          tilt_pannello, azimuth_pannello, 
                                          pitch_file, pitch_laterale):
        # Calcolo dinamico dell'ombreggiamento orario
        ombra_longitudinale = calculate_shadow_length(solpos, tilt_pannello, 
                                                     azimuth_pannello, panel_length)
        
        f_luce_ore = calculate_hourly_light_fraction(ombra_longitudinale, 
                                                   pitch_file, pitch_laterale, 
                                                   panel_length)
        
        E_suolo_ora = clearsky_ghi * f_luce_ore
        superficie_illuminata_ha = calculate_illuminated_area_per_hectare(
            f_luce_ore, pitch_file, pitch_laterale)
        
        E_suolo_tot_ha = (E_suolo_ora * superficie_illuminata_ha).sum() / 1000
        return E_suolo_ora, f_luce_ore, E_suolo_tot_ha
    ```

    **Metodologia**: Calcolo geometrico dell'ombreggiamento che considera:
    - Variazione della lunghezza dell'ombra durante il giorno
    - Geometria del campo fotovoltaico (pitch longitudinale e laterale)
    - Superficie effettivamente illuminata per ogni intervallo temporale

    **Output principale**: 
    - `E_suolo_tot_ha`: Radiazione solare totale che raggiunge il suolo [kWh/ha/giorno]
    - `f_luce_ore`: Frazione di superficie illuminata per ogni ora del giorno
    """)

    st.markdown("""
    ### 3.7 Validazione della Superficie

    **Implementazione**:
    ```python
    def validate_surface(num_panels, area):
        superficie_effettiva = num_panels * area
        gcr = superficie_effettiva / HECTARE_M2  # HECTARE_M2 = 10,000 m²
        
        is_valid = superficie_effettiva <= HECTARE_M2
        fattore_copertura_max = min(HECTARE_M2 / superficie_effettiva, 1.0) 
        
        return is_valid, fattore_copertura_max, superficie_effettiva, gcr
    ```

    **Parametri calcolati**:
    - **GCR (Ground Coverage Ratio)**: Rapporto tra area occupata dai pannelli e area totale
    - **Fattore di copertura massimo**: Fattore di scala per superfici > 1 ettaro
    """)

    st.markdown("---")

    # 4. OUTPUT E METRICHE
    st.markdown("""
    ## 4. Output e Metriche Principali

    ### 4.1 Metriche Energetiche
    - **Energia giornaliera pannelli (E_day)**: Produzione elettrica [kWh/ha/giorno]
    - **Radiazione suolo totale (E_suolo_tot_ha)**: Radiazione per coltivazioni [kWh/ha/giorno]
    - **Picco di potenza AC**: Potenza massima istantanea [kW]

    ### 4.2 Metriche Agro-FV  
    - **Frazione suolo illuminato medio**: Percentuale media di superficie illuminata [%]
    - **Ore di luce solare utile**: Ore con illuminazione > 10% [h/giorno]
    - **Rapporto radiazione suolo/GHI**: Efficienza di trasmissione luce [%]

    ### 4.3 Metriche Geometriche
    - **Ground Coverage Ratio (GCR)**: Densità di copertura del terreno [%]
    - **Superficie totale pannelli**: Area occupata dai moduli [m²]
    """)

    st.markdown("---")

    # 5. LIMITAZIONI E ASSUNZIONI
    st.markdown("""
    ## 5. Limitazioni e Assunzioni del Modello

    ### 5.1 Assunzioni Principali
    1. **Condizioni di cielo sereno**: I calcoli si basano sul modello Ineichen per condizioni atmosferiche ottimali
    2. **Temperatura ambiente costante**: 25°C per tutto il periodo di simulazione
    3. **Efficienza costante**: L'efficienza dei pannelli è considerata costante entro l'intervallo di temperatura operativo
    4. **Configurazione fissa**: I pannelli hanno orientamento e inclinazione fissi

    ### 5.2 Limitazioni Note
    - **Meteorologia reale**: Le condizioni nuvolose riducono significativamente la produzione effettiva
    - **Ombreggiamento tra file**: Non considerato nel calcolo della radiazione POA
    - **Effetti stagionali**: La simulazione è valida per il singolo giorno specificato
    - **Curva di efficienza**: Non considera la variazione di efficienza con l'irradianza

    ### 5.3 Accuratezza Attesa
    - **Condizioni di cielo sereno**: Errore stimato ±5% per la radiazione POA
    - **Produzione energetica**: Errore stimato ±10% considerando le semplificazioni del modello
    - **Radiazione al suolo**: Errore stimato ±15% per la natura geometrica del calcolo
    """)

    st.markdown("---")

    # 6. RIFERIMENTI BIBLIOGRAFICI
    st.markdown("""
    ## 6. Riferimenti Bibliograficici

    1. **Ineichen, P. & Perez, R.** (2002). "A new airmass independent formulation for the Linke turbidity coefficient"
    2. **Duffie, J.A. & Beckman, W.A.** (2013). "Solar Engineering of Thermal Processes", 4th Edition
    3. **IEC 61724-1**: (2017) "Photovoltaic system performance - Part 1: Monitoring"
    4. **IEC 61853-1**: (2011) "Photovoltaic module performance testing and energy rating"
    5. **PVLib Python Documentation**: https://pvlib-python.readthedocs.io/
    6. **Reda, I. & Andreas, A.** (2004). "Solar position algorithm for solar radiation applications"

    *Tutti i calcoli implementati seguono standard internazionali e best practices del settore.*
    """)

    st.markdown("---")

    # 7. NOTE TECNICHE
    st.markdown("""
    ## 7. Note Tecniche

    **Versione algoritmo**: 2.0  
    **Data ultima revisione**: """ + pd.Timestamp.now().strftime("%Y-%m-%d") + """  
    **Librerie principali**: PVLib Python, pandas, numpy  
    **Risoluzione temporale**: Oraria (24 punti per giorno)  
    **Unità di misura coerenti**: kW, kWh, m², gradi decimali

    *Per segnalazioni tecniche o richieste di implementazioni specifiche, contattare lo sviluppatore @ t.gasperini@univpm.it.*
    """)