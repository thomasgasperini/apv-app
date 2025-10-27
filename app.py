import streamlit as st
from config import CSS, PAGE_CONFIG, MESSAGES, HECTARE_M2
from sidebar import sidebar_inputs
from calculations import calculate_all_pv
from metrics import display_metrics
from maps import display_map_section
from guida import show_pv_guide

def setup_page():
    """Configura la pagina Streamlit e applica CSS globale"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CSS, unsafe_allow_html=True)

def main():
    """Funzione principale dell'applicazione"""
    setup_page()
    
    # Raccolta input da sidebar
    params = sidebar_inputs()
    
    # Mostra guida introduttiva
    show_pv_guide()
    
    # Esegui calcoli fotovoltaici completi
    results = calculate_all_pv(params)
    
    # Visualizzazione mappa e info impianto
    display_map_section(params)
    
    # Visualizzazione metriche
    display_metrics(results)

if __name__ == "__main__":
    main()
