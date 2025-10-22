# calculations.py
"""
Modulo per i calcoli fotovoltaici puri
- Posizione solare
- Irradianza
- Temperatura cella
- Potenza DC/AC
- Energia giornaliera
- Radiazione al suolo (Agro-FV)
"""

import pandas as pd
import pvlib
import numpy as np
from config import HECTARE_M2


def calculate_solar_position(times, lat, lon):
    """Calcola la posizione del sole"""
    return pvlib.solarposition.get_solarposition(times, lat, lon)


def calculate_clearsky_irradiance(times, lat, lon, timezone):
    """Calcola l'irradianza in condizioni di cielo sereno"""
    site = pvlib.location.Location(lat, lon, tz=timezone)
    return site.get_clearsky(times, model="ineichen")


def calculate_poa_irradiance(clearsky, solpos, tilt, azimuth, albedo):
    """Calcola l'irradianza sul piano del pannello (POA)"""
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
    """Calcola la temperatura della cella fotovoltaica"""
    return ambient_temp + (noct - 20) / 800 * poa_global


def calculate_dc_power(poa_global, area, eff, T_cell, temp_coeff, T_ref=25):
    """Calcola la potenza DC del pannello"""
    return poa_global * area * eff * (1 + temp_coeff * (T_cell - T_ref))


def calculate_ac_power(P_dc, losses):
    """Calcola la potenza AC dopo le perdite"""
    return P_dc * (1 - losses)


def calculate_ground_radiation(clearsky_ghi, panel_area, tilt, pitch_file, pitch_laterale):
    """
    Calcola la radiazione che raggiunge il suolo tra i pannelli
    considerando l'ombreggiamento dovuto a tilt e distanze
    """
    lato_pannello = np.sqrt(panel_area)
    lunghezza_proiezione = lato_pannello * np.sin(np.radians(tilt))
    
    # Frazione di luce tra le file
    f_luce_file = (pitch_file - lunghezza_proiezione) / pitch_file
    f_luce_file = np.clip(f_luce_file, 0, 1)
    
    # Frazione di luce laterale
    f_luce_lat = (pitch_laterale - lato_pannello) / pitch_laterale
    f_luce_lat = np.clip(f_luce_lat, 0, 1)
    
    # Frazione totale
    f_luce = f_luce_file * f_luce_lat
    
    # Radiazione al suolo
    E_suolo = clearsky_ghi * f_luce
    
    return E_suolo, f_luce


def calculate_coverage_factor(num_panels, pitch_laterale, pitch_file):
    """Calcola il fattore di copertura del terreno"""
    superficie_effettiva = num_panels * pitch_laterale * pitch_file
    return min(superficie_effettiva / HECTARE_M2, 1.0), superficie_effettiva


def validate_surface(superficie_effettiva):
    """Valida se la superficie supera 1 ettaro"""
    if superficie_effettiva > HECTARE_M2:
        fattore_copertura_max = HECTARE_M2 / superficie_effettiva
        return False, fattore_copertura_max
    return True, 1.0


def calculate_pv(params):
    """
    Funzione principale che orchestra tutti i calcoli fotovoltaici
    """
    # Generazione timeline
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # Validazione superficie
    fattore_copertura, superficie_effettiva = calculate_coverage_factor(
        params["num_panels"], params["pitch_laterale"], params["pitch_file"]
    )
    is_valid, fattore_copertura_max = validate_surface(superficie_effettiva)

    # Posizione solare
    solpos = calculate_solar_position(times, params["lat"], params["lon"])

    # Irradianza cielo sereno
    clearsky = calculate_clearsky_irradiance(
        times, params["lat"], params["lon"], params["timezone"]
    )

    # Irradianza sul pannello
    poa = calculate_poa_irradiance(
        clearsky, solpos, params["tilt"], params["azimuth"], params["albedo"]
    )

    # Temperatura cella
    T_cell = calculate_cell_temperature(poa['poa_global'], params["noct"])

    # Potenza DC
    P_dc = calculate_dc_power(
        poa['poa_global'], params["area"], params["eff"], T_cell, params["temp_coeff"]
    )

    # Potenza AC
    P_ac = calculate_ac_power(P_dc, params["losses"])

    # Energia giornaliera per ettaro
    E_day = P_ac.sum() * fattore_copertura_max / 1000  # kWh/ha

    # Radiazione al suolo (Agro-FV)
    E_suolo, f_luce = calculate_ground_radiation(
        clearsky['ghi'], params["area"], params["tilt"], 
        params["pitch_file"], params["pitch_laterale"]
    )
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
        "E_suolo": E_suolo,
        "E_suolo_tot": E_suolo_tot,
        "fattore_copertura": fattore_copertura,
        "f_luce": f_luce,
        "superficie_pannelli_tot": superficie_effettiva,
        "is_surface_valid": is_valid,
    }
