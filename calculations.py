# calculations.py
"""
Modulo per i calcoli fotovoltaici
- Validazione pannelli per ettaro
- Posizione solare
- Irradianza (clearsky e POA)
- Temperatura cella
- Potenza DC/AC
- Energia giornaliera
- Radiazione al suolo (Agro-FV)
"""

import pandas as pd
import numpy as np
import pvlib
from config import HECTARE_M2


def calculate_max_panels(area_panel, pitch_laterale, pitch_file):
    """
    Calcola il numero massimo di pannelli teorici che possono stare in 1 ettaro
    considerando pitch (distanza tra centri) e area pannello
    """
    # Area minima occupata per pannello = pitch_laterale * pitch_file
    area_per_panel = pitch_laterale * pitch_file
    max_panels = int(HECTARE_M2 // area_per_panel)
    return max_panels


def calculate_coverage(num_panels, pitch_laterale, pitch_file):
    """
    Calcola superficie effettiva occupata e fattore di copertura
    """
    superficie_effettiva = num_panels * pitch_laterale * pitch_file
    gcr = min(superficie_effettiva / HECTARE_M2, 1.0)
    return superficie_effettiva, gcr


def calculate_solar_position(times, lat, lon):
    return pvlib.solarposition.get_solarposition(times, lat, lon)


def calculate_clearsky_irradiance(times, lat, lon, timezone):
    site = pvlib.location.Location(lat, lon, tz=timezone)
    return site.get_clearsky(times, model="ineichen")


def calculate_poa_irradiance(clearsky, solpos, tilt, azimuth, albedo):
    return pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth'],
        albedo=albedo
    )


def calculate_cell_temperature(poa_global, noct, ambient_temp=25):
    return ambient_temp + (noct - 20)/800 * poa_global


def calculate_dc_power(poa_global, area, eff, T_cell, temp_coeff, T_ref=25):
    return poa_global * area * eff * (1 + temp_coeff * (T_cell - T_ref))


def calculate_ac_power(P_dc, losses):
    return P_dc * (1 - losses)


def calculate_ground_radiation(clearsky_ghi, panel_area, tilt, pitch_file, pitch_laterale):
    """
    Calcola la radiazione che raggiunge il suolo tra i pannelli
    considerando tilt e distanza tra file/pannelli
    """
    lato_pannello = np.sqrt(panel_area)
    lunghezza_proiezione = lato_pannello * np.sin(np.radians(tilt))

    f_luce_file = (pitch_file - lunghezza_proiezione)/pitch_file
    f_luce_file = np.clip(f_luce_file, 0, 1)

    f_luce_lat = (pitch_laterale - lato_pannello)/pitch_laterale
    f_luce_lat = np.clip(f_luce_lat, 0, 1)

    f_luce = f_luce_file * f_luce_lat
    E_suolo = clearsky_ghi * f_luce

    return E_suolo, f_luce


def validate_surface(num_panels, pitch_laterale, pitch_file):
    """
    Controlla se la superficie totale supera 1 ettaro
    """
    superficie_effettiva, gcr = calculate_coverage(num_panels, pitch_laterale, pitch_file)
    is_valid = superficie_effettiva <= HECTARE_M2
    fattore_copertura_max = min(HECTARE_M2 / superficie_effettiva, 1.0) if not is_valid else 1.0
    return is_valid, fattore_copertura_max, superficie_effettiva, gcr


def calculate_pv(params):
    """
    Funzione principale che esegue tutti i calcoli
    """
    # Timeline giornaliera oraria
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # Numero massimo pannelli consentito dall'ettaro
    max_panels = calculate_max_panels(params["area"], params["pitch_laterale"], params["pitch_file"])
    num_panels = min(params["num_panels"], max_panels)

    # Validazione superficie
    is_valid, fattore_copertura_max, superficie_effettiva, gcr = validate_surface(
        num_panels, params["pitch_laterale"], params["pitch_file"]
    )

    # Posizione solare
    solpos = calculate_solar_position(times, params["lat"], params["lon"])

    # Irradianza clearsky
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], params["timezone"])

    # Irradianza sul pannello (POA)
    poa = calculate_poa_irradiance(clearsky, solpos, params["tilt"], params["azimuth"], params["albedo"])

    # Temperatura cella
    T_cell = calculate_cell_temperature(poa['poa_global'], params["noct"])

    # Potenza DC
    P_dc = calculate_dc_power(poa['poa_global'], params["area"], params["eff"], T_cell, params["temp_coeff"])

    # Potenza AC
    P_ac = calculate_ac_power(P_dc, params["losses"])

    # Energia giornaliera per ettaro
    E_day = P_ac.sum() * fattore_copertura_max / 1000  # kWh/ha

    # Radiazione al suolo tra i pannelli (Agro-FV)
    E_suolo, f_luce = calculate_ground_radiation(clearsky['ghi'], params["area"], params["tilt"],
                                                 params["pitch_file"], params["pitch_laterale"])
    E_suolo_tot = E_suolo.sum() / 1000  # kWh/m²

    return {
        "num_panels": num_panels,
        "max_panels": max_panels,
        "is_surface_valid": is_valid,
        "fattore_copertura_max": fattore_copertura_max,
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr,
        "times": times,
        "solpos": solpos,
        "clearsky": clearsky,
        "poa": poa,
        "T_cell": T_cell,
        "P_dc": P_dc,
        "P_ac": P_ac,
        "E_day": E_day,
        "E_suolo": E_suolo,
        "E_suolo_tot": E_suolo_tot,
        "f_luce": f_luce
    }
