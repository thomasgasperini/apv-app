import streamlit as st

def show_pv_guide():
    """
    Mostra una guida tecnica completa sui calcoli fotovoltaici e sulla radiazione utile al suolo (Agro-FV),
    con formule, spiegazioni di ciascun termine e origine dei dati.
    """
    # Stato del pulsante
    if 'show_guide' not in st.session_state:
        st.session_state.show_guide = False

    # Pulsante per mostrare/nascondere la guida
    if st.button("📖 Mostra Guida PV"):
        st.session_state.show_guide = not st.session_state.show_guide

    if st.session_state.show_guide:
        # Introduzione
        st.markdown("""
        ## Guida Tecnica ai Calcoli Fotovoltaici

        Questa guida descrive in dettaglio come il modulo `calculations.py`:
        - Stima la radiazione incidente sui pannelli (POA)
        - Calcola la potenza DC e AC prodotta
        - Determina l'energia giornaliera per ettaro
        - Valuta la radiazione residua utile per coltivazioni sotto i pannelli (Agro-FV)
        """)

        st.markdown("---")

        # Flusso dei calcoli
        st.markdown("### 1. Flusso dei Calcoli")
        st.markdown("""
        1. Inserimento parametri da parte dell'utente:
           latitudine, longitudine, tilt e azimuth del modulo, area e efficienza,
           coefficiente di temperatura, pitch laterale e tra file, NOCT, perdite.
        2. Generazione della timeline oraria per il giorno selezionato.
        3. Calcolo della posizione solare (Zenith e Azimuth) tramite PVLib.
        4. Stima della radiazione teorica in cielo sereno (GHI, DNI, DHI) tramite PVLib.
        5. Calcolo della radiazione sul piano dei pannelli (POA) combinando radiazione diretta, diffusa e riflessa.
        6. Calcolo della temperatura della cella (T_cell) in funzione di POA e NOCT.
        7. Calcolo della potenza DC del modulo.
        8. Calcolo della potenza AC considerando le perdite del sistema.
        9. Somma della potenza AC per ottenere l'energia giornaliera per ettaro (E_day).
        10. Calcolo della frazione di luce che raggiunge il suolo (f_luce) e della radiazione residua utile (E_suolo).
        """)

        st.markdown("---")

        # Terminologia
        st.markdown("### 2. Terminologia e Definizioni")
        st.markdown("""
        - **GHI (Global Horizontal Irradiance):** radiazione totale su superficie orizzontale [W/m²]  
        - **DNI (Direct Normal Irradiance):** radiazione diretta perpendicolare ai raggi solari [W/m²]  
        - **DHI (Diffuse Horizontal Irradiance):** radiazione diffusa su superficie orizzontale [W/m²]  
        - **POA (Plane of Array Irradiance):** radiazione totale incidente sul piano inclinato dei pannelli  
        - **T_cell (Temperatura cella):** temperatura effettiva della cella, funzione di POA e NOCT  
        - **P_dc:** potenza DC generata dal modulo  
        - **P_ac:** potenza AC disponibile dopo le perdite di sistema  
        - **E_day:** energia giornaliera prodotta per ettaro [kWh/ha]  
        - **f_luce:** frazione di suolo illuminata tra le file di pannelli  
        - **E_suolo:** radiazione al suolo disponibile per coltivazioni [kWh/m²]
        """)

        st.markdown("---")

        # Formule principali
        st.markdown("### 3. Formule Principali")

        st.markdown("#### 3.1 Radiazione sul piano dei pannelli (POA)")
        st.latex(r"POA = DNI \cdot \cos(\theta_i) + DHI \cdot \frac{1 + \cos(\beta)}{2} + GHI \cdot \rho \cdot \frac{1 - \cos(\beta)}{2}")

        st.markdown("#### 3.2 Temperatura della cella")
        st.latex(r"T_{cell} = T_{amb} + \frac{NOCT - 20}{800} \cdot POA")

        st.markdown("#### 3.3 Potenza DC del modulo")
        st.latex(r"P_{dc} = POA \cdot A \cdot \eta \cdot \left(1 + \gamma (T_{cell}-25)\right)")

        st.markdown("#### 3.4 Potenza AC")
        st.latex(r"P_{ac} = P_{dc} \cdot (1 - losses)")

        st.markdown("#### 3.5 Energia giornaliera per ettaro")
        st.latex(r"E_{day} = \sum P_{ac} \cdot \Delta t")

        st.markdown("#### 3.6 Radiazione al suolo (Agro-FV)")
        st.latex(r"f_{luce} = \frac{pitch_{file} - p_{proj}}{pitch_{file}} \cdot \frac{pitch_{lat} - L}{pitch_{lat}}")
        st.latex(r"E_{suolo} = GHI \cdot f_{luce}")

        st.markdown("#### 3.7 Fattori geometrici")
        st.markdown("""
        - Superficie totale pannelli: numero_pannelli * pitch_laterale * pitch_file  
        - Fattore di copertura: superficie_totale / HECTARE_M2 (max = 1)
        """)

        st.markdown("---")

        # Origine dei dati
        st.markdown("### 4. Origine dei dati")
        st.markdown("""
        - **POA, GHI, DNI, DHI:** calcolati da PVLib Python (modello *ineichen* per cielo sereno)  
        - **Posizione solare (Zenith, Azimuth):** calcolata da PVLib  
        - **Parametri termici e geometrici:** forniti dall'utente (T_amb, NOCT, tilt, azimuth, area, efficienza, pitch)  
        - **f_luce e E_suolo:** calcolati geometricamente dal codice, basandosi su tilt, pitch e dimensioni dei pannelli  

        <div style='background-color:#f0f0f0;padding:10px;border-left:4px solid #0077b6;'>
        Nota: PVLib fornisce valori teorici derivati da modelli scientifici; per valori reali occorrerebbero misurazioni o dataset meteorologici.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Bibliografia
        st.markdown("### 5. Bibliografia")
        st.markdown("""
        - PVLib Python Documentation: [https://pvlib-python.readthedocs.io](https://pvlib-python.readthedocs.io)  
        - Duffie, J.A. & Beckman, W.A., *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013  
        - IEC 61853-1: *Photovoltaic module performance testing and energy rating*  
        - IEC 61724: *Photovoltaic system performance monitoring – Guidelines for measurement, data exchange, and analysis*
        """)
