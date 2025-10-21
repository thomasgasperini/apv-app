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
# 1️⃣ Titolo e descrizione
# -----------------------
st.set_page_config(page_title="PV Calculator", layout="wide")
st.title("☀️ Calcolatore Energia Pannello Fotovoltaico")
st.write("""
Questa app calcola l'energia prodotta da un pannello fotovoltaico in base al **comune**, 
alla data e ai parametri fisici del modulo.  
Utilizza modelli fisici di NREL e Sandia (via libreria *pvlib*).
""")

# -----------------------
# 2️⃣ Input utente
# -----------------------
st.sidebar.header("Parametri di Input")

# Geolocalizzazione del comune
comune = st.sidebar.text_input("Comune", value="Roma", help="Inserisci il nome del comune (es: Milano, Torino, Palermo...)")

geolocator = Nominatim(user_agent="pv_app")
location = geolocator.geocode(f"{comune}, Italia", timeout=10)

if location:
    lat = location.latitude
    lon = location.longitude

    # ✅ Fuso orario corretto con ZoneInfo
    timezone = ZoneInfo("Europe/Rome")

    st.sidebar.success(f"Coordinate trovate: lat {lat:.4f}, lon {lon:.4f}")
    st.sidebar.write(f"Fuso orario: `Europe/Rome` (gestione CET/CEST automatica)")
else:
    st.sidebar.error("Comune non trovato. Inserisci manualmente lat/lon.")
    lat = st.sidebar.number_input("Latitudine [°]", value=41.9)
    lon = st.sidebar.number_input("Longitudine [°]", value=12.5)
    timezone = ZoneInfo("Europe/Rome")

# Parametri pannello
tilt = st.sidebar.slider("Inclinazione β [°]", 0, 90, 30)
azimuth = st.sidebar.slider("Azimut del pannello [°]", -180, 180, 0,
                             help="0°=Sud, -90°=Est, +90°=Ovest")
area = st.sidebar.number_input("Area del pannello [m²]", value=1.6)
eff = st.sidebar.number_input("Efficienza del pannello [%]", value=20.0) / 100
albedo = st.sidebar.number_input("Albedo (riflessione del suolo)", value=0.2)
losses = st.sidebar.number_input("Perdite totali di sistema [%]", value=10.0) / 100
noct = st.sidebar.number_input("NOCT [°C]", value=45.0)
temp_coeff = st.sidebar.number_input("Coeff. temperatura [1/°C]", value=-0.004)
data = st.sidebar.date_input("Data", value=date(2025, 6, 21))

# -----------------------
# 3️⃣ Mappa interattiva
# -----------------------
if location:
    st.subheader("📍 Posizione del Comune")
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], tooltip=comune,
                  popup=f"{comune}\nLat: {lat:.4f}\nLon: {lon:.4f}").add_to(m)
    st_folium(m, width=700, height=400)

# -----------------------
# 4️⃣ Calcolo posizione solare e irradianza
# -----------------------
times = pd.date_range(
    start=datetime.combine(data, datetime.min.time()),
    end=datetime.combine(data, datetime.max.time()),
    freq="1h", tz=timezone)

# Posizione solare
solpos = pvlib.solarposition.get_solarposition(times, lat, lon)

# Modello cielo sereno (Ineichen)
site = pvlib.location.Location(lat, lon, tz=timezone)
clearsky = site.get_clearsky(times, model="ineichen")

# Irradianza su piano del modulo (Perez)
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

# -----------------------
# 5️⃣ Temperatura modulo (NOCT)
# -----------------------
T_amb = 25  # temperatura ambiente ipotetica
T_cell = T_amb + (noct - 20) / 800 * poa['poa_global']

# -----------------------
# 6️⃣ Potenza prodotta
# -----------------------
P_dc = poa['poa_global'] * area * eff * (1 + temp_coeff * (T_cell - 25))
P_ac = P_dc * (1 - losses)
E_day = P_ac.sum() / 1000  # Wh → kWh/giorno

# -----------------------
# 7️⃣ Visualizzazione risultati
# -----------------------
st.subheader("⚡️ Risultati giornalieri")

col1, col2, col3 = st.columns(3)
col1.metric("Energia prodotta", f"{E_day:.2f} kWh/giorno")
col2.metric("Picco di potenza", f"{P_ac.max():.1f} W")
col3.metric("Irradianza massima", f"{poa['poa_global'].max():.0f} W/m²")

# Grafico potenza
st.write("### Andamento della potenza oraria")
fig, ax = plt.subplots()
ax.plot(times, P_ac, label="Potenza AC [W]", color="orange")
ax.set_xlabel("Ora")
ax.set_ylabel("Potenza [W]")
ax.set_title(f"Produzione oraria stimata – {comune}")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# -----------------------
# 8️⃣ Tabella dati
# -----------------------
st.write("### Dati dettagliati (clicca per espandere)")
with st.expander("Mostra tabella dati"):
    df = pd.DataFrame({
        "Ora": times,
        "Zenith [°]": solpos['zenith'],
        "Azimut Sole [°]": solpos['azimuth'],
        "GHI [W/m²]": clearsky['ghi'],
        "POA [W/m²]": poa['poa_global'],
        "P_ac [W]": P_ac
    })
    st.dataframe(df.set_index("Ora").round(2))
