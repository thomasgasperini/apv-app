"""
Documentazione tecnica dei calcoli del simulatore fotovoltaico
"""

import streamlit as st


def show_pv_guide():
    """Visualizza documentazione tecnica completa in expander"""
    
    with st.expander("📘 GUIDA TECNICA - Documentazione Calcoli", expanded=False):
        st.markdown("""
        # DOCUMENTAZIONE TECNICA
        ## Simulatore Fotovoltaico Agrivoltaico
        
        ---
        
        ## 1. PARAMETRI DI INPUT
        
        ### 1.1 Localizzazione
        - **Comune**: testo inserito dall'utente
        - **Latitudine, Longitudine** [°]: calcolate automaticamente da `geopy.geocoders.Nominatim` tramite geocoding del comune. Se fallisce, richiesta manuale all'utente (default: 41.9, 12.5)
        - **Data simulazione**: `date.today()` o inserimento utente
        - **Timezone**: `ZoneInfo("Europe/Rome")`, fisso
        
        ### 1.2 Layout Pannelli
        - **Pannelli per fila**: input utente (default: 5)
        - **Numero file**: input utente (default: 2)
        - **Totale pannelli**: calcolato come $N_{tot} = N_{fila} \\times N_{file}$
        - **Lato maggiore** [m]: input utente (default: 2.5)
        - **Lato minore** [m]: input utente (default: 2.0)
        - **Area pannello** [m²]: calcolata come $A_{pan} = L_{mag} \\times L_{min}$
        
        ### 1.3 Geometria Installazione
        - **Distanza tra file (carreggiata)** [m]: input utente (default: 5.0)
        - **Pitch laterale** [m]: input utente (default: 3.0)
        - **Altezza dal suolo** [m]: input utente (default: 1.0)
        - **Tilt** [°]: input utente slider 0-90 (default: 30)
        - **Azimuth** [°]: input utente slider 0-360, 180=Sud (default: 180)
        
        ### 1.4 Caratteristiche Elettriche Pannelli
        - **Efficienza** [%]: input utente, conversione in frazione (default: 0.20)
        - **NOCT** [°C]: Nominal Operating Cell Temperature, input utente (default: 45)
        - **Coefficiente temperatura γ** [%/°C]: input utente (default: -0.004)
        - **Perdite sistema** [%]: input utente, conversione in frazione (default: 0.10)
        - **Albedo**: riflettanza suolo, input utente 0-1 (default: 0.2)
        
        ### 1.5 Parametri Campo
        - **Ettari totali**: input utente (default: 1.0)
        - **Superficie campo** [m²]: $A_{campo} = ettari \\times 10000$
        - **Tipo coltura**: selezione da lista predefinita (default: "Microgreens")
        
        ---
        
        ## 2. CALCOLI GEOMETRICI
        **Modulo**: `calculations.py` - `calculate_panel_metrics()`, `calculate_occupied_space()`
        
        ### 2.1 Proiezione Pannello al Suolo
        **Formula teorica**: 
        
        $$A_{proj} = A_{nominale} \\cdot \\cos(\\beta)$$
        
        dove $\\beta$ = tilt del pannello
        
        **Implementazione**:
        ```python
        proiezione_singolo = area_pannello * math.cos(math.radians(tilt_pannello))
        proiezione_totale = proiezione_singolo * num_panels_total
        ```
        
        ### 2.2 Ground Coverage Ratio (GCR)
        **Formula teorica**: 
        
        $$GCR = \\frac{A_{proiezione}}{A_{campo}}$$
        
        **Implementazione**:
        ```python
        superficie_campo = hectares * 10000
        gcr = proiezione_totale_pannelli / superficie_campo
        ```
        
        ### 2.3 Superficie Libera
        **Formula teorica**: 
        
        $$A_{libera} = A_{campo} - A_{proiezione}$$
        
        **Implementazione**:
        ```python
        superficie_libera = superficie_campo - proiezione_totale_pannelli
        ```
        
        ---
        
        ## 3. CALCOLI SOLARI
        **Modulo**: `calculations.py`  
        **Libreria principale**: `pvlib` (NREL)
        
        ### 3.1 Posizione Solare
        **Libreria**: `pvlib.solarposition.get_solarposition()`
        
        **Input**: `times` (pd.DatetimeIndex orario), `lat`, `lon`
        
        **Output**: DataFrame con elevation, azimuth, zenith del sole per ogni ora
        
        **Implementazione**:
        ```python
        solpos = pvlib.solarposition.get_solarposition(times, lat, lon)
        ```
        
        ### 3.2 Irradianza Cielo Sereno
        **Libreria**: `pvlib.location.Location.get_clearsky()`, modello Ineichen
        
        **Output**: GHI, DNI, DHI [W/m²] per ogni ora
        - **GHI**: Global Horizontal Irradiance (radiazione globale orizzontale)
        - **DNI**: Direct Normal Irradiance (radiazione diretta normale)
        - **DHI**: Diffuse Horizontal Irradiance (radiazione diffusa orizzontale)
        
        **Implementazione**:
        ```python
        site = pvlib.location.Location(lat, lon, tz=timezone)
        clearsky = site.get_clearsky(times, model="ineichen")
        ```
        
        ### 3.3 POA Global (Plane of Array)
        **Formula teorica**: 
        
        $$POA = POA_{direct} + POA_{diffuse} + POA_{reflected}$$
        
        **Libreria**: `pvlib.irradiance.get_total_irradiance()`
        
        **Input**: tilt, azimuth pannello, DNI, GHI, DHI, zenith/azimuth solare, albedo
        
        **Output**: irradianza sul piano del pannello [W/m²]
        
        **Implementazione**:
        ```python
        poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            dni=clearsky['dni'],
            ghi=clearsky['ghi'],
            dhi=clearsky['dhi'],
            solar_zenith=solpos['zenith'],
            solar_azimuth=solpos['azimuth'],
            albedo=albedo
        )
        poa_global = poa['poa_global']
        ```
        
        ### 3.4 Temperatura Ambiente
        **Modello**: sinusoidale empirico
        
        **Formula teorica**: 
        
        $$T_{amb}(h) = T_{media} + \\Delta T \\cdot \\sin\\left(\\frac{\\pi(h-6)}{12}\\right)$$
        
        dove:
        - $T_{media}$: temperatura media stagionale stimata per latitudine
        - $\\Delta T$: escursione termica giornaliera
        - $h$: ora del giorno (minimo h=6, massimo h=14)
        
        **Implementazione**:
        ```python
        T_amb = T_media + escursione * sin(π(h-6)/12)
        ```
        
        ---
        
        ## 4. CALCOLI PRODUZIONE ELETTRICA
        **Modulo**: `calculations.py` - `calculate_pv_production()`
        
        ### 4.1 Temperatura Celle
        **Formula teorica**: 
        
        $$T_{cell} = T_{amb} + \\frac{POA}{800} \\cdot (NOCT - 20)$$
        
        **Implementazione**:
        ```python
        T_cell = T_amb + (poa_global / 800) * (noct - 20)
        ```
        
        ### 4.2 Efficienza Corretta per Temperatura
        **Formula teorica**: 
        
        $$\\eta_{corr} = \\eta_{nom} \\cdot [1 + \\gamma \\cdot (T_{cell} - 25)]$$
        
        dove:
        - $\\eta_{nom}$: efficienza nominale a 25°C
        - $\\gamma$: coefficiente temperatura [1/°C]
        - $T_{cell}$: temperatura celle [°C]
        
        **Implementazione**:
        ```python
        eff_corr = eff * (1 + temp_coeff * (T_cell - 25))
        ```
        
        ### 4.3 Potenza Elettrica
        **Formula teorica**: 
        
        $$P = POA \\cdot A \\cdot \\eta_{corr} \\cdot (1 - perdite)$$
        
        **Implementazione**:
        ```python
        power_single_W = poa_global * area_pannello * eff_corr * (1 - losses)
        power_total_W = power_single_W * num_panels_total
        ```
        
        ### 4.4 Energia Giornaliera
        **Formula teorica**: 
        
        $$E_{day} = \\sum_{h=1}^{24} P_h \\quad [Wh]$$
        
        somma oraria su 24 ore
        
        **Implementazione**:
        ```python
        energy_single_Wh = power_single_W.sum()
        energy_total_Wh = power_total_W.sum()
        energy_total_Wh_m2 = energy_total_Wh / (area_pannello * num_panels_total)
        ```
        
        ---
        
        ## 5. CALCOLI AGRIVOLTAICI
        **Modulo**: `agri_calculations.py`
        
        ### 5.1 Proiezione Ombra Dinamica
        **Formule teoriche**:
        
        Altezza massima pannello:
        $$H = h_{suolo} + L_{min} \\cdot \\sin(\\beta)$$
        
        Lunghezza ombra:
        $$L_{ombra} = \\frac{H}{\\tan(\\theta_{sun})}$$
        
        Larghezza ombra:
        $$W_{ombra} = \\frac{A_{pannello} \\cdot \\cos(\\beta)}{L_{ombra}} \\cdot |\\cos(\\Delta\\phi)|$$
        
        Area ombra:
        $$A_{ombra} = L_{ombra} \\cdot W_{ombra}$$
        
        dove:
        - $h_{suolo}$: altezza base pannello da terra
        - $L_{min}$: lato minore pannello
        - $\\beta$: tilt pannello
        - $\\theta_{sun}$: elevazione solare (da pvlib)
        - $\\Delta\\phi$: differenza tra azimuth sole e pannello
        
        **Implementazione**:
        ```python
        H = altezza_suolo + lato_minore * sin(tilt_rad)
        L_shadow = H / tan(elevation_rad)
        W_shadow = (area_pannello * cos(tilt_rad)) / L_shadow * |cos(delta_azimuth_rad)|
        A_shadow = L_shadow * W_shadow
        ```
        
        ### 5.2 Frazione Ombreggiata del Campo
        **Formula teorica**: 
        
        $$f_{ombra} = \\frac{A_{ombra} \\cdot N_{pannelli}}{A_{campo}}$$
        
        clip a 1.0 (max 100%)
        
        **Implementazione**:
        ```python
        total_shadow_area = shadow_area_m2 * num_panels_total
        shaded_fraction = (total_shadow_area / superficie_campo).clip(upper=1.0)
        ```
        
        ### 5.3 Daily Light Integral (DLI)
        **Formule teoriche**:
        
        1. PAR disponibile:
        $$PAR = GHI \\cdot 0.45$$
        
        2. PAR pesata per ombreggiamento:
        $$PAR_{weighted} = PAR \\cdot (f_{ombra} \\cdot T_{under} + (1-f_{ombra}))$$
        
        dove $T_{under} = 0.15$ (trasmissione sotto pannello)
        
        3. Conversione in flusso fotonico:
        $$PAR_{\\mu mol} = PAR_{weighted} \\cdot 4.6 \\quad [\\mu mol/m^2/s]$$
        
        4. DLI giornaliero:
        $$DLI = \\frac{\\sum PAR_{\\mu mol} \\cdot 3600}{10^6} \\quad [mol/m^2/day]$$
        
        **Implementazione**:
        ```python
        par_total = ghi * 0.45
        par_weighted = par_total * (shaded_fraction * 0.15 + (1 - shaded_fraction))
        par_umol = par_weighted * 4.6
        dli_mol = (par_umol.sum() * 3600) / 1e6
        ```
        
        ### 5.4 Valutazione Adeguatezza Coltura
        **Requisiti DLI**: database interno (`DLI_REQUIREMENTS`) con $DLI_{min}$ e $DLI_{opt}$ per coltura
        
        **Formula teorica**: 
        
        $$Adeguatezza = \\frac{DLI_{misurato}}{DLI_{opt}} \\cdot 100$$
        
        **Classi di stato**:
        - Ottimale: ≥100%
        - Adeguato: 80-99%
        - Marginale: 60-79%
        - Insufficiente: <60%
        
        **Implementazione**:
        ```python
        percentage = (dli_value / DLI_opt) * 100
        # assegnazione status e colore in base a soglie
        ```
        
        ---
        
        ## 6. METRICHE OUTPUT
        
        ### 6.1 Irradiamento Solare
        - GHI, DNI, DHI: media oraria [W/m²] e totale giornaliero [Wh/m²]
        - POA: media oraria [W/m²] e totale giornaliero [Wh/m²]
        - T_cell_avg: temperatura media celle [°C]
        
        ### 6.2 Produzione Elettrica
        - Potenza singolo pannello: media oraria [W] e totale giornaliero [Wh]
        - Potenza totale impianto: media oraria [W] e totale giornaliero [Wh]
        - Produzione per m²: [Wh/m²]
        
        ### 6.3 Geometria e Copertura
        - Superficie totale pannelli [m²]: area nominale
        - Proiezione totale pannelli [m²]: ingombro al suolo
        - GCR: rapporto proiezione/campo (evidenziato se >0.4)
        - Superficie libera [m²]: terreno disponibile
        
        ### 6.4 Metriche Agronomiche
        - DLI totale giornaliero [mol/m²·day]
        - DLI richiesto: min e ottimale per coltura [mol/m²·day]
        - Adeguatezza luminosità [%]
        - Stato coltura: classificazione qualitativa
        - Ombreggiamento medio [%]: frazione media giornaliera
        - Ombra massima [m²]: picco durante il giorno
        
        ---
        
        ## 7. BIBLIOGRAFIA E RIFERIMENTI
        
        ### Librerie Software
        - **pvlib-python**: Holmgren et al. (2018). pvlib python: a python package for modeling solar energy systems. Journal of Open Source Software, 3(29), 884.
          https://pvlib-python.readthedocs.io/
        
        - **geopy**: GeoPy contributors. GeoPy: Geocoding library for Python.
          https://geopy.readthedocs.io/
        
        ### Modelli Solari
        - **Ineichen Clear Sky Model**: Ineichen, P. and Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.
        
        - **POA Irradiance Models**: Perez et al. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. Solar Energy, 44(5), 271-289.
        
        ### Modelli Fotovoltaici
        - **NOCT Temperature Model**: King et al. (2004). Photovoltaic array performance model. Sandia National Laboratories Report SAND2004-3535.
        
        - **Temperature Coefficient**: IEC 61215 standard for PV module performance testing.
        
        ### Agrivoltaico e DLI
        - **PAR Fraction**: Faust, J.E. and Logan, J. (2018). Daily light integral: A research review and high-resolution maps of the United States. HortScience, 53(9), 1250-1257.
        
        - **DLI Requirements**: Runkle, E. and Both, A.J. (2011). Greenhouse Energy Conservation Strategies. Michigan State University Extension.
        
        - **Shadow Projection**: Lorenzo, E. et al. (2011). Tracking and back-tracking. Progress in Photovoltaics, 19(6), 747-753.
        
        - **ENEA DLI Maps**: https://www.solaritaly.enea.it/DLI/
        
        ### Costanti Fisiche
        - **PAR Conversion**: 1 W/m² ≈ 4.6 μmol/m²/s (McCree, 1972. Test of current definitions of photosynthetically active radiation against leaf photosynthesis data. Agricultural Meteorology, 10, 443-453)
        
        ---
        
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="Guida Calcoli", layout="wide")
    show_pv_guide()