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

# -----------------------
# Aggiornamento repository
# -----------------------
# cd "C:\Users\Thomas\Desktop\Lavoro_050325\1) Progetti In Corso\Prova_Software_APV"
# git add app.py calculations.py config.py plots.py sidebar.py
# git status
# git add requirements.txt
# git commit -m "Rimuovi pywin32 per compatibilità Streamlit Cloud"
# git push origin main

# -----------------------
# Per avvio da terminal VSCode
# -----------------------
# cd "C:\Users\Thomas\Desktop\Lavoro_050325\1) Progetti In Corso\Prova_Software_APV"
# streamlit run app.py


import streamlit as st
from config import CSS
from sidebar import sidebar_inputs
from calculations import calculate_pv
from plots import plot_graphs
import pandas as pd

st.markdown(CSS, unsafe_allow_html=True)

# Input sidebar
params = sidebar_inputs()

# Calcoli PV
results = calculate_pv(params)

# Grafici e metriche
plot_graphs(params, results)

# Tabella dati
st.markdown('<p class="section-header">📋 Dati Orari Dettagliati</p>', unsafe_allow_html=True)
df = pd.DataFrame({
    "Ora": results["times"].strftime("%H:%M"),
    "POA [W/m²]": results["poa"]['poa_global'].round(0),
    "T_cell [°C]": results["T_cell"].round(1),
    "P_DC [W]": results["P_dc"].round(1),
    "P_AC [W]": results["P_ac"].round(1),
})
st.dataframe(df, use_container_width=True, height=400)

# Download CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica dati CSV",
    data=csv,
    file_name=f"pv_data_{params['comune']}_{params['data']}.csv",
    mime="text/csv"
)
