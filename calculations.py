"""
Modulo per calcoli fotovoltaici
Funzionalità:
- Calcolo posizione solare
- Calcolo irradianza (GHI, DNI, DHI, POA)
- Calcolo parametri geometrici (superficie, GCR)
"""

import pandas as pd
import pvlib
from config import HECTARE_M2

# ==================== CALCOLI GEOMETRICI ====================

def calculate_panel_area(base: float, altezza: float) -> float:
    """Calcola area singolo pannello [m²]."""
    return base * altezza

def calculate_coverage(num_panels: int, panel_area: float) -> tuple[float, float]:
    """
    Calcola superficie effettiva occupata e fattore di copertura (GCR).
    
    Args:
        num_panels: numero pannelli installati
        panel_area: area singolo pannello [m²]
    
    Returns:
        tuple: (superficie_effettiva [m²], gcr [0-1])
    """
    superficie_effettiva = num_panels * panel_area
    gcr = superficie_effettiva / HECTARE_M2
    return superficie_effettiva, gcr

# ==================== CALCOLI SOLARI ====================

def calculate_solar_position(times: pd.DatetimeIndex, lat: float, lon: float) -> pd.DataFrame:
    """Calcola posizione solare (zenith, azimuth) per timeline specificata."""
    return pvlib.solarposition.get_solarposition(times, lat, lon)

def calculate_clearsky_irradiance(times: pd.DatetimeIndex, lat: float, lon: float, timezone: str) -> pd.DataFrame:
    """Calcola irradianza in condizioni di cielo sereno (ghi, dni, dhi)."""
    site = pvlib.location.Location(lat, lon, tz=timezone)
    return site.get_clearsky(times, model="ineichen")

def calculate_poa_irradiance(clearsky: pd.DataFrame, solpos: pd.DataFrame,
                             tilt: float, azimuth: float, albedo: float) -> pd.DataFrame:
    """Calcola irradianza totale sul piano del modulo (POA)."""
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

# ==================== FUNZIONE PRINCIPALE ====================

def calculate_pv_basic(params: dict) -> dict:
    """
    Calcola tutti i parametri PV in W/m² e Wh/m² (giornalieri),
    con valori arrotondati a interi.
    """
    # Timeline oraria
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )
    
    # Superficie e GCR
    superficie_effettiva, gcr = calculate_coverage(params["num_panels"], params["area"])
    
    # Posizione solare e irradianza clearsky
    solpos = calculate_solar_position(times, params["lat"], params["lon"])
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], params["timezone"])
    
    # POA
    poa = calculate_poa_irradiance(
        clearsky, solpos,
        params["tilt_pannello"],
        params["azimuth_pannello"],
        params["albedo"]
    )
    
    # Arrotondamento a interi
    ghi_int = clearsky['ghi'].round(0).astype(int)
    dni_int = clearsky['dni'].round(0).astype(int)
    poa_int = poa['poa_global'].round(0).astype(int)
    
    # Valori giornalieri cumulativi (Wh/m²)
    return {
        "times": times,
        "GHI_Wm2": ghi_int,
        "DNI_Wm2": dni_int,
        "POA_Wm2": poa_int,
        "GHI_Whm2": ghi_int.sum(),
        "DNI_Whm2": dni_int.sum(),
        "POA_Whm2": poa_int.sum(),
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr
    }
