import pandas as pd
import pvlib
import numpy as np
import streamlit as st  # per mostrare warning direttamente

def calculate_pv(params):
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # --- Controllo superficie effettiva ---
    superficie_effettiva = params["num_panels"] * params["pitch_laterale"] * params["pitch_file"]
    if superficie_effettiva > 10000:
        st.warning(f"⚠️ La disposizione dei pannelli supera 1 ettaro! Superficie occupata: {superficie_effettiva:.0f} m²")
        # Limitiamo il fattore di copertura a 1 (ma avvertiamo l'utente)
        fattore_copertura_max = 10000 / superficie_effettiva
    else:
        fattore_copertura_max = 1.0

    # Posizione solare
    solpos = pvlib.solarposition.get_solarposition(times, params["lat"], params["lon"])

    # Cielo sereno
    site = pvlib.location.Location(params["lat"], params["lon"], tz=params["timezone"])
    clearsky = site.get_clearsky(times, model="ineichen")

    # Irradianza su pannello
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=params["tilt"],
        surface_azimuth=params["azimuth"],
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth'],
        albedo=params["albedo"]
    )

    # Temperatura cella
    T_cell = 25 + (params["noct"] - 20) / 800 * poa['poa_global']

    # Potenza su singolo pannello
    P_dc = poa['poa_global'] * params["area"] * params["eff"] * (1 + params["temp_coeff"]*(T_cell-25))
    P_ac = P_dc * (1 - params["losses"])

    # Energia giornaliera su 1 ha considerando fattore copertura massimo
    E_day = P_ac.sum() * fattore_copertura_max / 1000  # kWh/ha

    # --- Radiazione al suolo considerando pitch e tilt ---
    lato_pannello = np.sqrt(params["area"])
    lunghezza_proiezione = lato_pannello * np.sin(np.radians(params["tilt"]))
    f_luce_file = (params["pitch_file"] - lunghezza_proiezione) / params["pitch_file"]
    f_luce_file = np.clip(f_luce_file, 0, 1)
    f_luce_lat = (params["pitch_laterale"] - lato_pannello) / params["pitch_laterale"]
    f_luce_lat = np.clip(f_luce_lat, 0, 1)
    f_luce = f_luce_file * f_luce_lat  # Frazione luce totale

    E_suolo = clearsky['ghi'] * f_luce
    E_suolo_tot = E_suolo.sum() / 1000  # kWh/m² su 1 ha

    return {
        "times": times,
        "solpos": solpos,
        "clearsky": clearsky,
        "poa": poa,
        "T_cell": T_cell,
        "P_dc": P_dc,
        "P_ac": P_ac,
        "E_day": E_day,
        "E_suolo_tot": E_suolo_tot,
        "fattore_copertura": min(superficie_effettiva/10000, 1.0),
        "f_luce": f_luce,
        "superficie_pannelli_tot": superficie_effettiva
    }
