"""
Modulo Calcoli - Gestisce tutti i calcoli geometrici, solari ed elettrici
"""

import pandas as pd
import pvlib
import math
from config import HECTARE_M2


# ==================== CALCOLI GEOMETRICI ====================

def calculate_ground_projection(altezza: float, tilt: float) -> float:
    """
    Calcola proiezione a terra di un pannello inclinato
    
    Args:
        altezza: altezza pannello [m]
        tilt: inclinazione [°]
    
    Returns:
        proiezione a terra [m]
    """
    return altezza * math.cos(math.radians(tilt))


def calculate_panel_metrics(params: dict) -> dict:
    """
    Calcola metriche geometriche dei pannelli
    
    Args:
        params: dizionario parametri input
    
    Returns:
        dict con:
            - superficie_totale_pannelli: area nominale totale [m²]
            - proiezione_singolo: proiezione a terra singolo pannello [m²]
            - proiezione_totale: proiezione a terra tutti i pannelli [m²]
    """
    # Area nominale singolo pannello
    area_singolo = params["area_pannello"]
    
    # Area nominale totale
    superficie_totale = area_singolo * params["num_panels_total"]
    
    # Proiezione a terra singolo pannello
    proiezione_altezza = calculate_ground_projection(
        params["altezza_pannello"], 
        params["tilt_pannello"]
    )
    proiezione_singolo = params["base_pannello"] * proiezione_altezza
    
    # Proiezione totale
    proiezione_totale = proiezione_singolo * params["num_panels_total"]
    
    return {
        "superficie_totale_pannelli": superficie_totale,
        "proiezione_singolo_pannello": proiezione_singolo,
        "proiezione_totale_pannelli": proiezione_totale
    }


def calculate_inter_row_spacing(params: dict, panel_metrics: dict) -> dict:
    """
    Calcola spaziatura tra le file di pannelli
    
    Args:
        params: parametri input
        panel_metrics: metriche pannelli
    
    Returns:
        dict con:
            - spazio_libero_tra_file: spazio libero residuo tra file [m]
            - pitch_effettivo: pitch effettivamente utilizzato [m]
            - gcr_effettivo: GCR considerando il pitch [0-1]
    """
    # Proiezione in altezza del pannello inclinato
    proiezione_altezza = calculate_ground_projection(
        params["altezza_pannello"],
        params["tilt_pannello"]
    )
    
    # Lato minore (altezza proiettata) per il calcolo dello spazio libero
    lato_minore = proiezione_altezza

    # Spazio libero residuo tra colonne (formula richiesta)
    spazio_libero_tra_colonne = params["pitch_laterale"] - (lato_minore / 2)
    
    # Pitch effettivo (distanza tra assi delle file)
    pitch_effettivo = params["pitch_laterale"]


    return {
        "spazio_libero_tra_colonne": max(0, spazio_libero_tra_colonne),
        "pitch_effettivo": pitch_effettivo,
    }


def calculate_occupied_space(params: dict, panel_metrics: dict) -> dict:
    """
    Calcola spazio occupato sul terreno considerando layout reale
    
    Args:
        params: parametri input
        panel_metrics: metriche pannelli
    
    Returns:
        dict con:
            - gcr: Ground Coverage Ratio [0-1]
            - superficie_libera: spazio libero rimanente [m²]
    """
    # Superficie totale campo
    superficie_campo = params["hectares"] * HECTARE_M2
    
    # Calcola spaziatura tra file
    spacing_metrics = calculate_inter_row_spacing(params, panel_metrics)
    
    # GCR basato solo sulla proiezione pannelli (non layout completo)
    gcr = panel_metrics["proiezione_totale_pannelli"] / superficie_campo
    
    # Superficie libera
    superficie_libera = superficie_campo - panel_metrics["proiezione_totale_pannelli"]
    
    return {
        "gcr": gcr,
        "superficie_libera": max(0, superficie_libera),
        **spacing_metrics
    }


# ==================== CALCOLI SOLARI ====================

def calculate_solar_position(times: pd.DatetimeIndex, lat: float, lon: float) -> pd.DataFrame:
    """Calcola posizione solare"""
    return pvlib.solarposition.get_solarposition(times, lat, lon)


def calculate_clearsky_irradiance(times: pd.DatetimeIndex, lat: float, lon: float, tz: str) -> pd.DataFrame:
    """Calcola irradianza cielo sereno"""
    site = pvlib.location.Location(lat, lon, tz=tz)
    return site.get_clearsky(times, model="ineichen")


def calculate_poa_global(clearsky: pd.DataFrame, solpos: pd.DataFrame, 
                         tilt: float, azimuth: float, albedo: float) -> pd.Series:
    """
    Calcola POA (Plane of Array) globale
    
    Returns:
        Serie POA [W/m²]
    """
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
    return poa['poa_global'].round(0).astype(int)

def estimate_ambient_temperature(times: pd.DatetimeIndex, lat: float) -> pd.Series:
    """
    Stima temperatura ambiente oraria con modello sinusoidale
    
    Returns:
        Serie temperatura [°C]
    """
    month = times[0].month
    
    # Stima temperatura media stagionale
    if month in [12, 1, 2]:  # Inverno
        T_media = 8 - (lat - 40) * 0.5
        escursione = 6
    elif month in [3, 4, 5]:  # Primavera
        T_media = 15 - (lat - 40) * 0.3
        escursione = 8
    elif month in [6, 7, 8]:  # Estate
        T_media = 26 - (lat - 40) * 0.4
        escursione = 10
    else:  # Autunno
        T_media = 16 - (lat - 40) * 0.3
        escursione = 7
    
    # Temperatura oraria sinusoidale (min h6, max h14)
    hours = times.hour
    T_amb = T_media + escursione * pd.Series(
        [math.sin(math.pi * (h - 6) / 12) for h in hours],
        index=times
    )
    
    return T_amb


# ==================== CALCOLI PRODUZIONE ELETTRICA ====================

def calculate_pv_production(params: dict, poa_global: pd.Series, T_amb: pd.Series) -> dict:
    """
    Calcola produzione elettrica
    
    Args:
        params: parametri elettrici
        poa_global: radiazione POA [W/m²]
        T_amb: temperatura ambiente [°C]
    
    Returns:
        dict con:
            - power_single_W: potenza singolo pannello [W]
            - power_total_W: potenza totale [W]
            - energy_single_Wh: energia singolo pannello [Wh]
            - energy_total_Wh: energia totale [Wh]
            - energy_single_Wh_m2: energia/m² singolo [Wh/m²]
            - energy_total_Wh_m2: energia/m² totale [Wh/m²]
            - T_cell_avg: temperatura media celle [°C]
    """
    # Temperatura celle
    T_cell = T_amb + (poa_global / 800) * (params["noct"] - 20)
    
    # Efficienza corretta per temperatura
    eff_corr = params["eff"] * (1 + params["temp_coeff"] * (T_cell - 25))
    
    # Potenza istantanea singolo pannello [W]
    power_single = (
        poa_global * params["area_pannello"] * eff_corr * (1 - params["losses"])).round(0).astype(int)

    # Potenza totale [W]
    power_total = power_single * params["num_panels_total"]
    
    # Energia giornaliera
    energy_single = power_single.sum()
    energy_total = power_total.sum()
    
    # Energia per m²
    energy_total_m2 = energy_total / (params["area_pannello"] * params["num_panels_total"])
    
    return {
        "power_single_W": power_single,
        "power_total_W": power_total,
        "energy_single_Wh": energy_single,
        "energy_total_Wh": energy_total,
        "energy_total_Wh_m2": energy_total_m2,
        "T_cell_avg": T_cell.mean()
    }


# ==================== FUNZIONE PRINCIPALE ====================

def calculate_all_pv(params: dict) -> dict:
    """
    Calcola tutti i parametri PV
    
    Args:
        params: dizionario completo parametri input
    
    Returns:
        dict con tutti i risultati
    """
    # Serie temporale oraria
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )
    
    # Calcoli geometrici
    panel_metrics = calculate_panel_metrics(params)
    occupied_space = calculate_occupied_space(params, panel_metrics)
    
    # Calcoli solari
    solpos = calculate_solar_position(times, params["lat"], params["lon"])
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], str(params["timezone"]))
    poa_global = calculate_poa_global(clearsky, solpos, params["tilt_pannello"], 
                                      params["azimuth_pannello"], params["albedo"])
    T_amb = estimate_ambient_temperature(times, params["lat"])
    
    # Produzione elettrica
    production = calculate_pv_production(params, poa_global, T_amb)
    
    # Assemblaggio risultati
    return {
        # Serie temporali
        "times": times,
        "GHI_Wm2": clearsky['ghi'].round(0).astype(int),
        "DNI_Wm2": clearsky['dni'].round(0).astype(int),
        "DHI_Wm2": clearsky['dhi'].round(0).astype(int),
        "POA_Wm2": poa_global,
        "T_amb": T_amb.round(1),
        
        # Totali giornalieri
        "GHI_Whm2": clearsky['ghi'].sum().round(0).astype(int),
        "DNI_Whm2": clearsky['dni'].sum().round(0).astype(int),
        "DHI_Whm2": clearsky['dhi'].sum().round(0).astype(int),
        "POA_Whm2": poa_global.sum().round(0).astype(int),
        
        # Metriche geometriche
        **panel_metrics,
        **occupied_space,
        
        # Produzione elettrica
        **production
    }