"""
Modulo principale dell'applicazione PV Simulator
Orchestrazione di tutti i componenti:
- Configurazione pagina Streamlit
- Raccolta input utente (sidebar)
- Esecuzione calcoli fotovoltaici
- Visualizzazione risultati (guida, mappa, metriche)
"""

import streamlit as st
from config import CSS, PAGE_CONFIG, MESSAGES, HECTARE_M2
from sidebar import sidebar_inputs
from calculations import calculate_pv_basic
from metrics import display_metrics
from maps import display_map_section
from guida import show_pv_guide

# ==================== CONFIGURAZIONE INIZIALE ====================

def setup_page():
    """Configura la pagina Streamlit e applica CSS globale"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CSS, unsafe_allow_html=True)


# ==================== FUNZIONE PRINCIPALE ====================

def main():
    """
    Funzione principale dell'applicazione
    Coordina tutti i moduli in sequenza logica
    """
    # Setup iniziale
    setup_page()
    
    # Raccolta input da sidebar
    params = sidebar_inputs()
    
    # Mostra guida introduttiva
    show_pv_guide()
    
    # Esegui calcoli fotovoltaici
    results = calculate_pv_basic(params)
    
    # Visualizzazione mappa e info impianto
    display_map_section(params)
    
    # Visualizzazione metriche
    display_metrics(params, results)


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    main()
