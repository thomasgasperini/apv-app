# app.py
"""
Modulo principale di orchestrazione
- Configurazione pagina
- Coordinamento tra moduli
- Visualizzazione risultati
"""

import streamlit as st
import pandas as pd
from config import CSS, PAGE_CONFIG, MESSAGES
from sidebar import sidebar_inputs
from calculations import calculate_pv
from metrics import display_metrics
from maps import display_map_section
from plots import display_charts
from guida import show_pv_guide


# ===== CONFIGURAZIONE PAGINA =====
st.set_page_config(**PAGE_CONFIG)

# Applica CSS globale
st.markdown(CSS, unsafe_allow_html=True)


# ===== RACCOLTA INPUT =====
params = sidebar_inputs()

# Mostra guida PV
show_pv_guide()


# ===== CALCOLI FOTOVOLTAICI =====
results = calculate_pv(params)

# Warning se superficie supera 1 ettaro
if not results["is_surface_valid"]:
    st.warning(MESSAGES["surface_exceed"].format(
        superficie=results["superficie_pannelli_tot"]
    ))


# ===== VISUALIZZAZIONE MAPPA =====
display_map_section(params)


# ===== VISUALIZZAZIONE METRICHE =====
display_metrics(params, results)


# ===== VISUALIZZAZIONE GRAFICI =====
display_charts(params, results)


# ===== TABELLA DATI DETTAGLIATI =====
st.markdown('<p class="section-header">📋 Dati Orari Dettagliati</p>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Ora": results["times"].strftime("%H:%M"),
    "POA [W/m²]": results["poa"]['poa_global'].round(0),
    "P_DC [W]": results["P_dc"].round(1),
    "P_AC [W]": results["P_ac"].round(1),
})

st.dataframe(df, use_container_width=True, height=400)


# ===== DOWNLOAD CSV =====
st.markdown(
    """
    <style>
    div.stDownloadButton button {
        background-color: #74a65b;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica dati CSV",
    data=csv,
    file_name=f"pv_data_{params['comune']}_{params['data']}.csv",
    mime="text/csv"
)
