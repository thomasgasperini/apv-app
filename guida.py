# guida.py
import streamlit as st

def show_pv_guide():
    """
    Mostra una guida dettagliata con tutte le equazioni utilizzate nei calcoli PV
    e le relative fonti bibliografiche, direttamente in Streamlit.
    Visualizzazione tramite pulsante elegante, non più un expander.
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
        ## 1. Posizione Solare
        La posizione del sole viene calcolata come funzione di latitudine, longitudine e tempo:
        $$\\text{Solar Zenith, Solar Azimuth} = f(\\text{latitudine, longitudine, tempo})$$
        dove:
        - Zenith = angolo tra il sole e la verticale locale  
        - Azimuth = direzione del sole rispetto al Nord  
        **Fonte:** PVLib Python - [Solar Position](https://pvlib-python.readthedocs.io/en/stable/solarposition.html)

        ## 2. Irradianza sul Pannello (POA)
        Irradianza totale sul piano del pannello (POA):
        $$POA = DNI \\cdot \\cos(\\theta_i) + DHI \\cdot \\frac{1 + \\cos(\\beta)}{2} + GHI \\cdot \\rho \\cdot \\frac{1 - \\cos(\\beta)}{2}$$
        dove:
        - $\\theta_i$ = angolo di incidenza del sole sul pannello  
        - $\\beta$ = tilt del pannello  
        - $\\rho$ = albedo del terreno  
        - DNI = Direct Normal Irradiance, DHI = Diffuse Horizontal Irradiance, GHI = Global Horizontal Irradiance  
        **Fonte:** Duffie & Beckman, *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013

        ## 3. Temperatura della Cella
        $$T_{cell} = T_{amb} + \\frac{NOCT - 20}{800} \\cdot POA$$
        dove:
        - $T_{amb}$ = temperatura ambiente (°C), tipicamente 25°C come riferimento  
        - NOCT = Nominal Operating Cell Temperature  
        - POA = Irradianza sul piano del pannello  
        **Fonte:** PVLib Python Documentation

        ## 4. Potenza DC del Modulo
        $$P_{dc} = POA \\cdot A \\cdot \\eta \\cdot \\left(1 + \\gamma (T_{cell}-25)\\right)$$
        dove:
        - $A$ = area del modulo (m²)  
        - $\\eta$ = efficienza del modulo  
        - $\\gamma$ = coefficiente di temperatura (%/°C)  
        - $T_{cell}$ = temperatura della cella  
        **Fonte:** Standard Photovoltaic Module Model, IEC 61853-1

        ## 5. Potenza AC
        $$P_{ac} = P_{dc} \\cdot (1 - \\text{losses})$$
        dove:
        - losses = perdite totali del sistema (inverter, cablaggi, mismatch, ombreggiamento, polvere, ecc.)  
        **Fonte:** Standard PV System Modeling, IEC 61724

        ## 6. Energia Giornaliera
        $$E_{day} = \\sum P_{ac} \\cdot \\Delta t$$
        dove $\\Delta t$ = intervallo temporale tra due misurazioni consecutive (tipicamente 1h).  
        **Fonte:** Calcolo numerico orario basato su PVLib

        ## Bibliografia
        - PVLib Python Documentation: [https://pvlib-python.readthedocs.io/](https://pvlib-python.readthedocs.io/)  
        - Duffie, J.A. & Beckman, W.A., *Solar Engineering of Thermal Processes*, 4th Edition, Wiley, 2013  
        - IEC 61853-1: *Photovoltaic (PV) module performance testing and energy rating*  
        - IEC 61724: *Photovoltaic system performance monitoring – Guidelines for measurement, data exchange, and analysis*  
        """, unsafe_allow_html=True)
