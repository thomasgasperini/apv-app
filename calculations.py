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


def calculate_coverage(num_panels, area):
    """
    Calcola superficie effettiva occupata e fattore di copertura
    """
    superficie_effettiva = num_panels * area
    gcr = superficie_effettiva / HECTARE_M2
    return superficie_effettiva, gcr


def calculate_solar_position(times, lat, lon):
    return pvlib.solarposition.get_solarposition(times, lat, lon)


def calculate_clearsky_irradiance(times, lat, lon, timezone):
    site = pvlib.location.Location(lat, lon, tz=timezone)
    return site.get_clearsky(times, model="ineichen")


def calculate_poa_irradiance(clearsky, solpos, tilt_pannello, azimuth_pannello, albedo):
    return pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt_pannello,
        surface_azimuth=azimuth_pannello,
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
    # Convertiamo da W a kW dividendo per 1000
    return (poa_global * area * eff * (1 + temp_coeff * (T_cell - T_ref))) / 1000


def calculate_ac_power(P_dc, losses):
    # P_dc è già in kW, manteniamo in kW
    return P_dc * (1 - losses)


def calculate_ground_radiation_improved(clearsky_ghi, solpos, panel_area, tilt_pannello, 
                                      azimuth_pannello, pitch_file, pitch_laterale, 
                                      surface_tilt_ground=0):
    """
    Calcola migliorato della radiazione che raggiunge il suolo considerando:
    - Ombreggiamento dinamico durante il giorno
    - Geometria reale delle file
    - Superficie libera tra i pannelli
    """
    lato_pannello = np.sqrt(panel_area)
    
    # Calcola la proiezione dell'ombra per ogni ora del giorno
    ombra_longitudinale = calculate_shadow_length(solpos, tilt_pannello, azimuth_pannello, lato_pannello)
    
    # Frazione di superficie illuminata per ogni ora
    f_luce_ore = calculate_hourly_light_fraction(ombra_longitudinale, pitch_file, pitch_laterale, lato_pannello)
    
    # Radiazione effettiva al suolo per ogni ora (W/m²)
    E_suolo_ora = clearsky_ghi * f_luce_ore
    
    # Calcola la superficie totale illuminata per ettaro
    superficie_illuminata_ha = calculate_illuminated_area_per_hectare(
        f_luce_ore, pitch_file, pitch_laterale
    )
    
    # Energia totale che raggiunge il suolo per ettaro (kWh/ha)
    E_suolo_tot_ha = (E_suolo_ora * superficie_illuminata_ha).sum() / 1000  # kWh/ha
    
    return E_suolo_ora, f_luce_ore, E_suolo_tot_ha


def calculate_shadow_length(solpos, tilt, azimuth, panel_length):
    """
    Calcola la lunghezza dell'ombra proiettata dai pannelli per ogni ora
    """
    # Angolo di incidenza solare sul piano dei pannelli
    cos_theta_i = pvlib.irradiance.aoi(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth']
    )
    
    # Evita valori NaN per cos_theta_i negativi (notte)
    cos_theta_i = np.clip(cos_theta_i, 0, 1)
    
    # Lunghezza ombra longitudinale (direzione tilt)
    shadow_longitudinal = panel_length * np.sin(np.radians(tilt)) * cos_theta_i
    
    # Lunghezza ombra laterale (dipende dall'azimuth solare)
    azimuth_diff = np.abs(solpos['azimuth'] - azimuth)
    shadow_lateral = panel_length * np.sin(np.radians(azimuth_diff)) * 0.3  # Fattore riduttivo
    
    return pd.DataFrame({
        'longitudinal': shadow_longitudinal,
        'lateral': shadow_lateral
    }, index=solpos.index)


def calculate_hourly_light_fraction(shadows, pitch_file, pitch_laterale, panel_length):
    """
    Calcola la frazione di luce che raggiunge il suolo per ogni ora
    considerando ombreggiamento longitudinale e laterale
    """
    # Frazione luce longitudinale (direzione tilt)
    f_luce_longitudinal = (pitch_file - shadows['longitudinal']) / pitch_file
    f_luce_longitudinal = np.clip(f_luce_longitudinal, 0, 1)
    
    # Frazione luce laterale
    f_luce_lateral = (pitch_laterale - shadows['lateral'] - panel_length) / pitch_laterale
    f_luce_lateral = np.clip(f_luce_lateral, 0, 1)
    
    # Frazione luce totale (prodotto delle due direzioni)
    f_luce_totale = f_luce_longitudinal * f_luce_lateral
    
    return f_luce_totale


def calculate_illuminated_area_per_hectare(f_luce_ore, pitch_file, pitch_laterale):
    """
    Calcola la superficie illuminata per ettaro per ogni ora
    """
    # Area di terreno per pannello (m²)
    area_terreno_per_pannello = pitch_file * pitch_laterale
    
    # Numero di "spazi pannello" per ettaro
    num_spazi_per_ha = HECTARE_M2 / area_terreno_per_pannello
    
    # Superficie illuminata per ettaro per ogni ora (m²/ha)
    superficie_illuminata_ha = f_luce_ore * HECTARE_M2
    
    return superficie_illuminata_ha


def validate_surface(num_panels, area):
    """
    Controlla se la superficie totale supera 1 ettaro
    """
    superficie_effettiva, gcr = calculate_coverage(num_panels, area)
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

    num_panels = params["num_panels"]
    area = params["area"]

    # Validazione superficie
    is_valid, fattore_copertura_max, superficie_effettiva, gcr = validate_surface(num_panels, area)

    # Posizione solare
    solpos = calculate_solar_position(times, params["lat"], params["lon"])

    # Irradianza clearsky
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], params["timezone"])

    # Irradianza sul pannello (POA)
    poa = calculate_poa_irradiance(
        clearsky, solpos,
        params["tilt_pannello"],
        params["azimuth_pannello"],
        params["albedo"]
    )

    # Temperatura cella
    T_cell = calculate_cell_temperature(poa['poa_global'], params["noct"])

    # Potenza DC (ora in kW invece di W)
    P_dc = calculate_dc_power(poa['poa_global'], area, params["eff"], T_cell, params["temp_coeff"])

    # Potenza AC (ora in kW invece di W)
    P_ac = calculate_ac_power(P_dc, params["losses"])

    # Energia giornaliera per ettaro (ora più semplice)
    E_day = P_ac.sum() * fattore_copertura_max  # kWh/ha (già in kW)

    # RADIAZIONE AL SUOLO MIGLIORATA (Agro-FV)
    E_suolo_ora, f_luce_ore, E_suolo_tot_ha = calculate_ground_radiation_improved(
        clearsky['ghi'], solpos, area,
        params["tilt_pannello"],
        params["azimuth_pannello"],
        params["pitch_file"],
        params["pitch_laterale"]
    )

    return {
        "num_panels": num_panels,
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
        "E_day": E_day,            # kWh/ha - Energia prodotta dai pannelli
        "E_suolo": E_suolo_ora,    # W/m² - Radiazione oraria al suolo
        "E_suolo_tot_ha": E_suolo_tot_ha,  # kWh/ha - Radiazione TOTALE al suolo per ettaro
        "f_luce": f_luce_ore       # Frazione di luce oraria
    }