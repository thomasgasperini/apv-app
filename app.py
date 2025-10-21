import streamlit as st
import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from datetime import datetime, date
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from zoneinfo import ZoneInfo  # ✅ Fuso orario corretto
from guida import show_pv_guide
from config import CSS
from sidebar import sidebar_inputs
from calculations import calculate_pv
from plots import plot_graphs

# Applica il CSS globale
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------
# Sidebar: Inputs + Guida
# -----------------------

params = sidebar_inputs()

show_pv_guide()  # Mostra pulsante per aprire la guida in nuova scheda

# -----------------------
# Calcoli PV
# -----------------------
results = calculate_pv(params)

# -----------------------
# Grafici e metriche
# -----------------------
plot_graphs(params, results)

# -----------------------
# Tabella Dati
# -----------------------
st.markdown('<p class="section-header">📋 Dati Orari Dettagliati</p>', unsafe_allow_html=True)
df = pd.DataFrame({
    "Ora": results["times"].strftime("%H:%M"),
    "POA [W/m²]": results["poa"]['poa_global'].round(0),
    "P_DC [W]": results["P_dc"].round(1),
    "P_AC [W]": results["P_ac"].round(1),
})
st.dataframe(df, use_container_width=True, height=400)

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

# Bottone download
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica dati CSV",
    data=csv,
    file_name=f"pv_data_{params['comune']}_{params['data']}.csv",
    mime="text/csv"
)

