import streamlit as st
from config import CSS, PAGE_CONFIG
from sidebar import sidebar_inputs
from calculations import calculate_all_pv
from metrics import display_metrics
from maps import display_map_section
from guida import show_pv_guide
from agri_calculations import calculate_all_agri

def setup_page():
    """Configura la pagina Streamlit e applica CSS globale"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CSS, unsafe_allow_html=True)

def main():
    """Funzione principale dell'applicazione"""
    setup_page()

    # --- Collect user inputs ---
    params = sidebar_inputs()
    
    show_pv_guide()
    
    # --- PV calculations ---
    results = calculate_all_pv(params)

    # --- Agricultural calculations (requires PV results) ---
    agri_results = calculate_all_agri(params, results)
    
    # Merge agricultural results into PV results
    results["agri_results"] = agri_results

    # --- Debug: show selected crop ---
    st.write(f"Selected crop: {params['crops']}")
    
    # --- Map and metrics ---
    display_map_section(params)
    display_metrics(results, params)

if __name__ == "__main__":
    main()