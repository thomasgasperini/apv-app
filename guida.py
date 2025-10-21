# guida.py
import streamlit as st

def show_pv_guide():
    """
    Mostra una guida dettagliata con tutte le equazioni utilizzate nei calcoli PV,
    la logica dei calcoli e le relative fonti bibliografiche, direttamente in Streamlit.
    Visualizzazione tramite pulsante elegante.
    """
    # Stato del pulsante
    if 'show_guide' not in st.session_state:
        st.session_state.show_guide = False

    # Pulsante per mostrare/nascondere la guida
    if st.button("📖 Mostra Guida PV"):
        st.session_state.show_guide = not st.session_state.show_guide

    # Mostra contenuto solo se stato attivo
    if st.session_state.show_guide:
        st.markdown("""
        ## Guida ai Calcoli Fotovoltaici

        Questa guida spiega la logica dei calcoli utilizzati per simulare la produzione elettrica 
        di un impianto fotovoltaico, distinguendo tra energia solare incidente, energia prodotta e 
        radiazione utile per coltivazioni sotto i pannelli (Agro-FV).

        ### 1. Posizione Solare
        La posizione del sole dipende da latitudine, longitudine e ora del giorno:
        $$\\text{Solar Zenith}, \\text{Solar Azimuth} = f(\\text{latitudine, longitudine, tempo})$$
        - **Zenith**: angolo tra il sole e la verticale locale  
        - **Azimuth**: direzione del sole rispetto al Nord  
        **Fonte:** [PVLib Solar Position](https://pvlib-python.readthedocs.io/en/stable/solarposition.html)

        ### 2. Irradianza sul Piano dei Pannelli (POA)
        L'irradianza totale sul pannello combina:
        - componente diretta (DNI)
        - componente diffusa (DHI)
        - riflessione dal terreno (GHI * albedo)

        $$POA = DNI \\cdot \\cos(\\theta_i) + DHI \\cdot \\frac{1 + \\cos(\\beta)}{2} + GHI \\cdot \\rho \\cdot \\frac{1 - \\cos(\\beta)}{2}$$
        dove:
        - $\\theta_i$: angolo di incidenza dei raggi solari sul pannello  
        - $\\beta$: tilt del pannello  
        - $\\rho$: albedo del terreno  
        - DNI, DHI, GHI: componenti solari misurate  
        **Fonte:** Duffie & Beckman, *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013

        ### 3. Temperatura della Cella
        La temperatura effettiva della cella influenza l'efficienza:
        $$T_{cell} = T_{amb} + \\frac{NOCT - 20}{800} \\cdot POA$$
        - $T_{amb}$: temperatura ambiente (°C)  
        - NOCT: temperatura nominale della cella a condizioni standard  
        - POA: irradiamento sul piano pannello  
        **Fonte:** PVLib Python

        ### 4. Potenza DC del Modulo
        La potenza elettrica generata dal modulo dipende da area, efficienza e temperatura:
        $$P_{dc} = POA \\cdot A \\cdot \\eta \\cdot \\left(1 + \\gamma (T_{cell}-25)\\right)$$
        - $A$: area del modulo [m²]  
        - $\\eta$: efficienza del modulo  
        - $\\gamma$: coefficiente di temperatura (%/°C)  
        - $T_{cell}$: temperatura effettiva della cella  
        **Fonte:** IEC 61853-1

        ### 5. Potenza AC
        Considerando le perdite di sistema (inverter, cablaggi, mismatch, sporco):
        $$P_{ac} = P_{dc} \\cdot (1 - \\text{losses})$$
        - losses: percentuale di perdite totali del sistema  
        **Fonte:** IEC 61724

        ### 6. Energia Giornaliera
        L'energia giornaliera prodotta si calcola sommando la potenza AC istantanea:
        $$E_{day} = \\sum P_{ac} \\cdot \\Delta t$$
        - $\\Delta t$: intervallo temporale (tipicamente 1 h)  
        - Valore espresso in kWh/ha  
        **Fonte:** Calcolo numerico basato su PVLib

        ### 7. Energia Solare Disponibile al Suolo (Agro-FV)
        Considera l'ombra dei pannelli e il pitch tra file/pannelli:
        $$E_{suolo} = GHI \\cdot f_{luce}$$
        - $f_{luce}$: frazione di suolo illuminata  
        - Serve per valutare coltivazioni sotto i pannelli (Agro-FV)

        ### 8. Fattori Geometrici
        - **Area Totale Pannelli:** superficie fisica dei pannelli installati  
        - **Superficie Effettiva Occupata:** include spazi tra file  
        - **Land Area Occupation Ratio:** rapporto tra pannelli e area del sito  
        - **Tilt / Azimuth / Pitch:** orientamento e disposizione pannelli  
        - **Albedo / Perdite:** riflettanza del terreno e perdite complessive impianto

        ### Bibliografia
        - PVLib Python Documentation: [https://pvlib-python.readthedocs.io/](https://pvlib-python.readthedocs.io/)  
        - Duffie, J.A. & Beckman, W.A., *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013  
        - IEC 61853-1: *Photovoltaic module performance testing and energy rating*  
        - IEC 61724: *Photovoltaic system performance monitoring – Guidelines for measurement, data exchange, and analysis*
        """, unsafe_allow_html=True)
