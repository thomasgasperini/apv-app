"""
Modulo per calcoli fotovoltaici
Funzionalità:
- Calcolo posizione solare
- Calcolo irradianza (GHI, DNI, DHI, POA globale)
- Calcolo parametri geometrici (superficie, GCR)
- Calcolo produzione elettrica dei pannelli
"""

import pandas as pd
import pvlib
from config import HECTARE_M2
import math

# ==================== CALCOLI GEOMETRICI ====================

def calculate_panel_area(base_pannello: float, altezza_pannello: float) -> float:
    """Calcola area singolo pannello [m²]."""
    return base_pannello * altezza_pannello

def calculate_coverage(num_panels: int, panel_area: float) -> tuple[float, float]:
    """Calcola superficie effettiva e GCR"""
    superficie_effettiva = num_panels * panel_area
    gcr = superficie_effettiva / HECTARE_M2
    return superficie_effettiva, gcr

def calculate_empty_space_per_hectare(base_pannello: float, altezza_pannello: float, tilt: float, 
                                       pitch_laterale: float, pitch_verticale: float, 
                                       pannelli_per_fila: int, num_file: int):
    """
    Calcola lo spazio vuoto all'interno di un ettaro dato layout pannelli, pitch e tilt.
    Usa HECTARE_M2 dalla configurazione.

    Args:
        base_pannello (float): lato minore del pannello [m]
        altezza_pannello (float): lato maggiore del pannello [m]
        tilt (float): inclinazione pannello [°]
        pitch_laterale (float): distanza tra centri pannelli affiancati [m]
        pitch_verticale (float): distanza tra centri pannelli su file diverse [m]
        pannelli_per_fila (int): numero di pannelli per fila
        num_file (int): numero di file di pannelli

    Returns:
        dict: {
            "spazio_vuoto_laterale": m,
            "spazio_vuoto_verticale": m,
            "larghezza_totale": m,
            "altezza_totale": m,
            "superficie_occupata": m²,
            "superficie_vuota": m²
        }
    """
    # Proiezione lato maggiore a terra
    altezza_effettiva = altezza_pannello * math.cos(math.radians(tilt))

    # Spazio vuoto tra pannelli
    spazio_vuoto_laterale = max(0, pitch_laterale - base_pannello)
    spazio_vuoto_verticale = max(0, pitch_verticale - altezza_effettiva)

    # Dimensioni totali occupate
    larghezza_totale = pannelli_per_fila * base_pannello + (pannelli_per_fila - 1) * spazio_vuoto_laterale
    altezza_totale = num_file * altezza_effettiva + (num_file - 1) * spazio_vuoto_verticale

    superficie_occupata = larghezza_totale * altezza_totale
    superficie_vuota = max(0, HECTARE_M2 - superficie_occupata)

    return {
        "spazio_vuoto_laterale": spazio_vuoto_laterale,
        "spazio_vuoto_verticale": spazio_vuoto_verticale,
        "larghezza_totale": larghezza_totale,
        "altezza_totale": altezza_totale,
        "superficie_occupata": superficie_occupata,
        "superficie_vuota": superficie_vuota
    }

# ==================== CALCOLI SOLARI ====================

def calculate_solar_position(times: pd.DatetimeIndex, lat: float, lon: float) -> pd.DataFrame:
    return pvlib.solarposition.get_solarposition(times, lat, lon)

def calculate_clearsky_irradiance(times: pd.DatetimeIndex, lat: float, lon: float, timezone: str) -> pd.DataFrame:
    site = pvlib.location.Location(lat, lon, tz=timezone)
    return site.get_clearsky(times, model="ineichen")

def calculate_poa_global(clearsky: pd.DataFrame, solpos: pd.DataFrame,
                         tilt: float, azimuth: float, albedo: float) -> pd.Series:
    """Calcola POA globale [W/m²] sul piano dei pannelli"""
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

# ==================== CALCOLO PV BASE ====================

def calculate_pv_basic(params: dict) -> dict:
    """Calcola GHI, DNI, DHI, POA globale [W/m²] e Wh/m² giornalieri"""
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    superficie_effettiva, gcr = calculate_coverage(params["num_panels"], params["area"])

    solpos = calculate_solar_position(times, params["lat"], params["lon"])
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], params["timezone"])

    poa_global = calculate_poa_global(clearsky, solpos, params["tilt_pannello"], params["azimuth_pannello"], params["albedo"])

    return {
        "times": times,
        "GHI_Wm2": clearsky['ghi'].round(0).astype(int),
        "DNI_Wm2": clearsky['dni'].round(0).astype(int),
        "DHI_Wm2": clearsky['dhi'].round(0).astype(int),
        "POA_global_Wm2": poa_global,
        "GHI_Whm2": clearsky['ghi'].sum().round(0).astype(int),
        "DNI_Whm2": clearsky['dni'].sum().round(0).astype(int),
        "DHI_Whm2": clearsky['dhi'].sum().round(0).astype(int),
        "POA_Whm2": poa_global.sum().round(0).astype(int),
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr
    }

# ==================== CALCOLO PRODUZIONE ELETTRICA ====================

def calculate_pv_production(params: dict, poa_global: pd.Series) -> dict:
    """Calcola produzione elettrica istantanea [W] e giornaliera [Wh]"""
    T_cell = 25 + (poa_global / 800) * (params["noct"] - 20)
    eff_corr = params["eff"] * (1 + params["temp_coeff"] * (T_cell - 25))

    P_inst = poa_global * params["area"] * params["num_panels"] * eff_corr * (1 - params["losses"])
    P_inst = P_inst.round(0).astype(int)
    E_day = P_inst.sum()

    return {
        "PV_power_W": P_inst,
        "PV_energy_Wh": E_day
    }

# ==================== FUNZIONE TUTTI I CALCOLI ====================

def calculate_all_pv(params: dict) -> dict:
    """
    Calcola tutti i parametri fotovoltaici principali per un giorno:

    Parametri:
        params (dict): dizionario contenente tutti i parametri di input
                       (geometria pannelli, sistema elettrico, lat/lon, data, ecc.)

    Restituisce:
        dict: {
            times: DatetimeIndex,
            GHI_Wm2, DNI_Wm2, DHI_Wm2: irradiance istantanea [W/m²],
            POA_global_Wm2: POA sul piano dei pannelli [W/m²],
            GHI_Whm2, DNI_Whm2, DHI_Whm2, POA_Whm2: energia giornaliera [Wh/m²],
            superficie_effettiva: superficie totale pannelli [m²],
            gcr: Ground Coverage Ratio,
            PV_power_W: potenza istantanea [W],
            PV_energy_Wh: energia giornaliera [Wh]
        }
    """
    # ------------------- 1. Calcolo base PV -------------------
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # Superficie effettiva e GCR
    superficie_effettiva, gcr = calculate_coverage(params["num_panels"], params["area"])

    # Posizione solare e irradianza clearsky
    solpos = calculate_solar_position(times, params["lat"], params["lon"])
    clearsky = calculate_clearsky_irradiance(times, params["lat"], params["lon"], params["timezone"])

    # POA globale sul piano dei pannelli
    poa_global = calculate_poa_global(
        clearsky, solpos, params["tilt_pannello"], params["azimuth_pannello"], params["albedo"]
    )

    # ------------------- 2. Calcolo produzione elettrica -------------------
    production = calculate_pv_production(params, poa_global)

    # ------------------- 3. Preparazione risultato -------------------
    results = {
        "times": times,
        "GHI_Wm2": clearsky['ghi'].round(0).astype(int),
        "DNI_Wm2": clearsky['dni'].round(0).astype(int),
        "DHI_Wm2": clearsky['dhi'].round(0).astype(int),
        "POA_global_Wm2": poa_global,
        "GHI_Whm2": clearsky['ghi'].sum().round(0).astype(int),
        "DNI_Whm2": clearsky['dni'].sum().round(0).astype(int),
        "DHI_Whm2": clearsky['dhi'].sum().round(0).astype(int),
        "POA_Whm2": poa_global.sum().round(0).astype(int),
        "superficie_effettiva": superficie_effettiva,
        "gcr": gcr,
        "PV_power_W": production["PV_power_W"],
        "PV_energy_Wh": production["PV_energy_Wh"]
    }

    return results