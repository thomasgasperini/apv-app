"""
Modulo Guida - Documentazione Tecnica e Operativa del Simulatore Agrivoltaico.
Fornisce una panoramica dettagliata e professionale dei modelli di calcolo utilizzati.
"""

import streamlit as st

try:
    from config import TIMEZONE
except ImportError:
    TIMEZONE = "Europe/Rome"

# ==================== CONTENUTO DELLE TAB ====================

def tab_introduzione():
    """Contenuto per la tab Introduzione e Flusso Operativo."""
    st.markdown("""
    ### 📚 Introduzione al Simulatore Agrivoltaico
    
    Il simulatore è uno strumento avanzato per l'analisi tecnico-economica di impianti agrivoltaici, 
    integrando la produzione fotovoltaica con l'agricoltura sostenibile. Permette di valutare simultaneamente:
    
    - ⚡ **Prestazioni energetiche** dell'impianto fotovoltaico
    - 🌱 **Impatto agronomico** sulle colture sottostanti
    - 📐 **Ottimizzazione geometrica** del layout
    
    ---
    
    ### 🎯 Obiettivi della Simulazione
    
    Il simulatore risponde a domande fondamentali per la progettazione agrivoltaica:
    
    1. **Quanta energia produce l'impianto?** Analisi oraria della produzione elettrica considerando irraggiamento, temperatura e perdite di sistema.
    2. **Come influisce l'ombreggiamento sulle colture?** Calcolo dinamico della frazione ombreggiata durante il giorno.
    3. **Le colture ricevono luce sufficiente?** Valutazione del DLI (Daily Light Integral) rispetto ai fabbisogni colturali.
    4. **Come ottimizzare il layout?** Analisi dello spazio occupato, GCR e superficie libera per l'agricoltura.
    
    ---
    
    ### 🔬 Fondamenti Scientifici
    
    Il simulatore si basa su quattro pilastri scientifici:
    
    #### 1. Modellazione Solare
    Algoritmi validati calcolano:
    - Posizione del sole (elevazione e azimuth) in funzione di coordinate geografiche, data e ora
    - Irradianza in condizioni di cielo sereno (modello Ineichen-Perez)
    - Componenti diretta, diffusa e globale della radiazione
    
    #### 2. Energetica Fotovoltaica
    Modelli termoelettrici per:
    - Calcolo della temperatura delle celle solari (modello NOCT)
    - Correzione dell'efficienza in funzione della temperatura
    - Stima delle perdite di sistema (cavi, inverter, sporcizia)
    
    #### 3. Geometria Tridimensionale
    Calcoli avanzati di trigonometria per:
    - Proiezione dell'ombra in tempo reale
    - Sovrapposizione tra file di pannelli
    - Distribuzione spaziale della radiazione al suolo
    
    #### 4. Agronomia Quantitativa
    Valutazione della compatibilità colturale tramite:
    - Integrazione del PAR (Photosynthetically Active Radiation)
    - Calcolo del DLI considerando ombreggiamento e trasmissività
    - Confronto con soglie specifiche per ogni specie
    
    ---
    
    ### 🛠️ Tecnologie e Librerie
    
    Il simulatore si basa su uno stack tecnologico robusto, con l'impiego di librerie specializzate:
    
    | Libreria | Ruolo |
    |----------|-------|
    | **pvlib** | Modellazione fotovoltaica con algoritmi NASA/NREL |
    | **pandas** | Gestione serie temporali e analisi dati |
    | **geopy** | Geocoding e conversione località → coordinate |
    | **streamlit** | Interfaccia web interattiva |
    | **folium** | Mappe georeferenziate interattive |
    | **shapely** | Calcoli geometrici 2D |
    
    ---
    
    ### 📊 Flusso Operativo della Simulazione
    
    ```
    1. INPUT UTENTE (sidebar.py)
       • Localizzazione e Geometria
       • Parametri Elettrici e Colturali
       ↓
    2. CALCOLI FOTOVOLTAICI (calculations.py)
       • Posizione solare oraria (pvlib.solarposition)
       • Irradianza clearsky (pvlib.clearsky)
       • POA (trasposizione sul piano inclinato)
       • Temperatura celle (modello NOCT)
       • Potenza DC/AC con correzione efficienza
       ↓
    3. CALCOLI AGRIVOLTAICI (agri_calculations.py)
       • Proiezione ombra dinamica (trigonometria 3D)
       • Frazione ombreggiata e sovrapposizione file
       • PAR disponibile modulato per ombra
       • DLI giornaliero
       • Valutazione coltura rispetto alle soglie
       ↓
    4. OUTPUT METRICHE (metrics.py)
       • KPI energetici e agronomici visualizzati in card
       • Grafici temporali e indicatori di performance
    ```
    """)

def tab_input_utente():
    """Contenuto per la tab Input Utente."""
    st.markdown("""
    ## 📥 Dettaglio Input Utente (Modulo `sidebar.py`)
    
    Il modulo raccoglie tutti i parametri di configurazione necessari alla simulazione.
    
    ---
    
    ### 🌍 Localizzazione e Data
    
    | Parametro | Descrizione | Implementazione |
    |-----------|------------|----------------|
    | Comune | Località della simulazione | Geocoding tramite `geopy.Nominatim` con caching |
    | Latitudine e Longitudine | Coordinate geografiche del sito | Derivate dal Geocoding o inserite manualmente |
    | Data | Giorno della simulazione | Serie temporale oraria (24 ore) |
    
    ### ⚙️ Parametri Pannelli
    
    - **Dimensioni:** `Lato Maggiore [m]`, `Lato Minore [m]` → area pannello
    - **Layout:** `Pannelli per Fila`, `Numero File` → totale moduli
    - **Orientamento:** `Tilt [°]`, `Azimuth [°]` (180° = Sud)
    - **Spaziatura:** `Carreggiata [m]`, `Pitch Laterale [m]`
    - **Altezza dal suolo [m]**
    
    ### ⚡ Sistema Elettrico
    
    - **Efficienza nominale e coeff. termico ($\gamma$ [%/°C])**
    - **Temperatura NOCT [°C]**
    - **Perdite di sistema [%]**
    - **Albedo del suolo (0-1)**
    
    ### 🌽 Parametri Agricoli
    
    - **Superficie:** Ettari Totali
    - **Coltura:** Tipo di coltura → requisiti DLI specifici
    """)

def tab_calculations():
    """Contenuto per la tab Calcoli Energetici e Geometrici."""
    st.markdown(r"""
    ## ⚡ Calcoli PV e Geometria (Modulo `calculations.py`)
    
    ---
    
    ### 📐 Calcoli Geometrici e Layout
    
    - **Proiezione a Terra:** $A_{proj} = A_{pannello} \cdot \cos(\text{Tilt})$
    - **Superficie Libera:** Area Totale Campo − Proiezione Totale Pannelli
    - **Ground Cover Ratio (GCR):** frazione di suolo coperta
      $$\text{GCR} = \frac{\text{Proiezione Totale Pannelli}}{\text{Superficie Totale Campo}}$$
    
    ### ☀️ Calcoli Solari
    
    - Posizione Solare oraria: `pvlib.solarposition.get_solarposition`
    - Irradianza Clearsky: `pvlib.location.Location.get_clearsky(model="ineichen")`
    - Irradianza sul piano inclinato (POA): `pvlib.irradiance.get_total_irradiance`
    
    ### 🌡️ Calcoli Produzione Elettrica
    
    - **Temperatura Celle (NOCT):**
      $$T_{cell} = T_{amb} + \frac{\text{POA}_{\text{global}}}{800} \cdot (NOCT - 20)$$
    - **Efficienza corretta:**
      $$\eta_{corr} = \eta \cdot [1 + \gamma \cdot (T_{cell} - 25)]$$
    - **Potenza DC:**
      $$\text{Potenza}_{DC} = \text{POA}_{\text{global}} \cdot A_{pannello} \cdot \eta_{corr} \cdot (1 - \text{Perdite})$$
    """)

def tab_agri_calculations():
    """Contenuto per la tab Calcoli Agrivoltaici e Bibliografia."""
    st.markdown(r"""
    ## 🌱 Calcoli Agrivoltaici (Modulo `agri_calculations.py`)
    
    ---
    
    ### 🌑 Ombreggiamento Dinamico
    
    - **Altezza effettiva:** $H = \text{Altezza suolo} + L_{minore} \cdot \sin(\text{Tilt})$
    - **Lunghezza ombra:** $L_{ombra} = \frac{H}{\tan(\alpha)}$
    - **Frazione ombreggiata:** area ombra corretta per sovrapposizione file
    
    ### 🌾 Daily Light Integral (DLI)
    
    - **Conversione GHI → PAR:** $\text{PAR}_{totale} = \text{GHI} \cdot 0.45$
    - **PAR pesato per ombra:** 
      $$\text{PAR}_{pesato} = \text{PAR}_{totale} \cdot [(\text{Frazione Ombra} \cdot T_{sotto}) + (1 - \text{Frazione Ombra}) \cdot T_{libera}]$$
    - **DLI finale:**
      $$\text{DLI} = \frac{\sum (\text{PAR}_{pesato} \cdot 4.6) \cdot 3600}{10^6}$$
    
    ### 🎯 Valutazione Agronomica
    Confronto DLI calcolato con soglie minime e ottimali per la coltura
    
    ---
    
    ## 📚 Bibliografia
    
    - Perez et al., *Modeling daylight availability and irradiance components*, Solar Energy, 1990
    - NREL, *Solar Position Algorithm*
    - IEC 61215:2016, *Nominal Operating Cell Temperature*
    - McCree, *The action spectrum and quantum yield of photosynthesis*, Agricultural Meteorology, 1972
    - Database CEA per requisiti DLI colturali
    """)

# ==================== FUNZIONE PRINCIPALE ====================

def show_pv_guide():
    """
    Funzione principale per visualizzare la guida tecnica completa in un expander con tab.
    """

    with st.expander("🔬 Dettaglio Tecnico e Scientifico del Simulatore", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs([
            "Introduzione e Flusso", 
            "Input Utente", 
            "Calcoli PV & Geometria", 
            "Calcoli Agronomici & Bibliografia"
        ])
        
        with tab1:
            tab_introduzione()
        
        with tab2:
            tab_input_utente()
            
        with tab3:
            tab_calculations()
            
        with tab4:
            tab_agri_calculations()
