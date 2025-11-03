"""
Modulo Calcoli Agricoli - Parametri agrivoltaico (microclima rimosso)
Analizza l'impatto dei pannelli FV sulle colture sottostanti (solo radiazione)
"""

import pandas as pd
import numpy as np
import math
from config import HECTARE_M2

# ==================== COSTANTI AGRONOMICHE ====================

TRANSMISSION_COEFF = {
    "under_panel": 0.15,
    "between_rows": 1.0,
    "edge_effect": 0.3
}

PAR_FRACTION = 0.45  # PAR = 45% GHI

DLI_REQUIREMENTS = {
    "Piante basse": {
        "Microgreens": {"DLI_min": 8, "DLI_opt": 12, "unit": "mol/m²/d"},
        "Ortaggi a foglia": {"DLI_min": 12, "DLI_opt": 18, "unit": "mol/m²/d"},
        "Tuberi": {"DLI_min": 15, "DLI_opt": 20, "unit": "mol/m²/d"},
        "Ortaggi da frutto bassi": {"DLI_min": 18, "DLI_opt": 22, "unit": "mol/m²/d"},
    },
    "Piante alte": {
        "Cereali": {"DLI_min": 20, "DLI_opt": 25, "unit": "mol/m²/d"},
        "Legumi": {"DLI_min": 15, "DLI_opt": 20, "unit": "mol/m²/d"},
        "Ortaggi da frutto alti": {"DLI_min": 22, "DLI_opt": 30, "unit": "mol/m²/d"},
        "Frutta (alberi e arbusti)": {"DLI_min": 22, "DLI_opt": 28, "unit": "mol/m²/d"},
        "Viti": {"DLI_min": 20, "DLI_opt": 25, "unit": "mol/m²/d"},
        "Piante ornamentali alte": {"DLI_min": 10, "DLI_opt": 15, "unit": "mol/m²/d"},
    }
}

# ==================== CALCOLO OMBRA DINAMICA ====================
def calculate_shadow_projection(lato_maggiore: float, lato_minore: float,
                                tilt: float, azimuth_panel: float,
                                sun_elevation: pd.Series, sun_azimuth: pd.Series,
                                altezza_suolo: float) -> pd.DataFrame:

    tilt_rad = math.radians(tilt)
    area_pannello = lato_maggiore * lato_minore

    # Altezza punto più alto
    H = altezza_suolo + lato_minore * math.sin(tilt_rad)

    shadow_length, shadow_width, shadow_area = [], [], []

    for elev, azim in zip(sun_elevation, sun_azimuth):
        if elev <= 0:
            shadow_length.append(0)
            shadow_width.append(0)
            shadow_area.append(0)
            continue

        elev_rad = math.radians(elev)
        delta_azimuth = abs(azim - azimuth_panel)
        if delta_azimuth > 180:
            delta_azimuth = 360 - delta_azimuth

        # Lunghezza ombra determinata dall'altezza reale
        L_shadow = H / math.tan(elev_rad)

        # Larghezza come proiezione dell'area sull'asse perpendicolare alla luce
        W_shadow = (area_pannello * math.cos(tilt_rad)) / max(L_shadow, 1e-6)

        # Correzione per orientamento rispetto al sole
        W_shadow *= abs(math.cos(math.radians(delta_azimuth)))

        A_shadow = L_shadow * W_shadow

        shadow_length.append(L_shadow)
        shadow_width.append(W_shadow)
        shadow_area.append(A_shadow)

    return pd.DataFrame({
        'shadow_length_m': shadow_length,
        'shadow_width_m': shadow_width,
        'shadow_area_m2': shadow_area
    }, index=sun_elevation.index)


def calculate_shaded_fraction(shadow_df: pd.DataFrame, num_panels: int, superficie_campo: float) -> pd.Series:
    total_shadow_area = shadow_df['shadow_area_m2'] * num_panels
    shaded_fraction = total_shadow_area / superficie_campo
    return shaded_fraction.clip(upper=1.0)

# ==================== RADIAZIONE DISPONIBILE ====================

def calculate_par_distribution(ghi: pd.Series, shaded_fraction: pd.Series,
                               transmission_under: float = TRANSMISSION_COEFF["under_panel"]) -> dict:

    par_total = ghi * PAR_FRACTION
    par_under = par_total * transmission_under
    par_between = par_total * TRANSMISSION_COEFF["between_rows"]

    par_weighted = par_under * shaded_fraction + par_between * (1 - shaded_fraction)

    return {
        "PAR_under_panels_umol": par_under * 4.6,
        "PAR_between_rows_umol": par_between * 4.6,
        "PAR_weighted_umol": par_weighted * 4.6,
        "PAR_weighted_W": par_weighted
    }


def calculate_dli(par_weighted_umol: pd.Series) -> float:
    return (par_weighted_umol.sum() * 3600) / 1e6


def evaluate_crop_suitability(par_under_umol: pd.Series,
                              par_between_umol: pd.Series,
                              par_weighted_umol: pd.Series,
                              crop_name: str) -> dict:

    def get_crop_requirement(name: str):
        for category, crops in DLI_REQUIREMENTS.items():
            if name in crops:
                return crops[name]
        return None

    requirement_data = get_crop_requirement(crop_name)

    if requirement_data is None:
        import streamlit as st
        st.warning(f"⚠️ Crop '{crop_name}' non trovato in DLI_REQUIREMENTS. Uso valori di default 100 mol/m²/d.")
        DLI_min, DLI_opt = 80, 100  # default values
        unit = "mol/m²/d"
    else:
        DLI_min = requirement_data["DLI_min"]
        DLI_opt = requirement_data["DLI_opt"]
        unit = requirement_data["unit"]

    # Calcolo DLI giornaliero
    dli_under = (par_under_umol.sum() * 3600) / 1e6
    dli_between = (par_between_umol.sum() * 3600) / 1e6
    dli_weighted = (par_weighted_umol.sum() * 3600) / 1e6

    def _dli_status(dli_value):
        percentage = (dli_value / DLI_opt) * 100
        if percentage >= 100:
            status, color = "Ottimale", "green"
        elif percentage >= 80:
            status, color = "Adeguato", "orange"
        elif percentage >= 60:
            status, color = "Marginale", "darkorange"
        else:
            status, color = "Insufficiente", "red"
        return {"dli": dli_value, "percentage": percentage, "status": status, "color": color, "unit": unit}

    return {
        "under_panels": _dli_status(dli_under),
        "between_rows": _dli_status(dli_between),
        "field_weighted": _dli_status(dli_weighted),
        "DLI_min": DLI_min,
        "DLI_opt": DLI_opt,
        "unit": unit
    }

# ==================== UNIFORMITÀ LUMINOSA ====================

def calculate_light_uniformity(par_under: pd.Series, par_between: pd.Series) -> float:
    """
    Calcola l'uniformità della luce sul campo agrivoltaico.
    
    L'uniformità è definita come 1 - (deviazione standard / media) della PAR
    combinata tra sotto i pannelli e tra le file. Restituisce un valore tra 0 e 1:
        - 1 = luce perfettamente uniforme
        - 0 = luce molto disomogenea

    Args:
        par_under (pd.Series): PAR sotto i pannelli (μmol/m²/s)
        par_between (pd.Series): PAR tra le file di pannelli (μmol/m²/s)

    Returns:
        float: indice di uniformità della luce sul campo (0-1)
    """
    all_par = pd.concat([par_under, par_between])
    mean = all_par.mean()
    std = all_par.std()
    if mean > 0:
        return max(0, 1 - std / mean)
    return 0

# ==================== FUNZIONE PRINCIPALE ====================

def calculate_all_agri(params: dict, pv_results: dict) -> dict:

    times = pv_results['times']
    ghi = pv_results['GHI_Wm2']
    superficie_campo = params['hectares'] * HECTARE_M2
    solpos = pv_results["solpos"]

    shadow_df = calculate_shadow_projection(
        lato_maggiore=params['lato_maggiore'],
        lato_minore=params['lato_minore'],
        tilt=params['tilt_pannello'],
        azimuth_panel=params['azimuth_pannello'],
        sun_elevation=solpos['elevation'],
        sun_azimuth=solpos['azimuth'],
        altezza_suolo=params['altezza_suolo']
    )

    shaded_fraction = calculate_shaded_fraction(
        shadow_df, params['num_panels_total'], superficie_campo
    )

    par_data = calculate_par_distribution(ghi, shaded_fraction)

    dli = calculate_dli(par_data['PAR_weighted_umol'])
    crop_eval = evaluate_crop_suitability(
        par_data['PAR_under_panels_umol'],
        par_data['PAR_between_rows_umol'],
        par_data['PAR_weighted_umol'],
        params.get("crops", "Cereali")
    )


    uniformity = calculate_light_uniformity(
        par_data['PAR_under_panels_umol'], par_data['PAR_between_rows_umol']
    )

    return {
        "times": times,
        "shaded_fraction": shaded_fraction,
        "shadow_length_m": shadow_df['shadow_length_m'],
        "shadow_area_m2": shadow_df['shadow_area_m2'],

        "PAR_under_panels_umol": par_data['PAR_under_panels_umol'],
        "PAR_between_rows_umol": par_data['PAR_between_rows_umol'],
        "PAR_weighted_umol": par_data['PAR_weighted_umol'],

        # Metriche ombra
        "shaded_fraction_avg": shaded_fraction.mean(),
        "shadow_area_max_m2": shadow_df['shadow_area_m2'].max(),
        "shadow_length_max_m": shadow_df['shadow_length_m'].max(),

        # DLI
        "DLI_mol_m2_day": dli,
        "PAR_daily_avg_umol": par_data['PAR_weighted_umol'].mean(),

        # Stato coltura
        "crop_status": crop_eval["field_weighted"]["status"],
        "crop_status_color": crop_eval["field_weighted"]["color"],
        "crop_light_adequacy_pct": crop_eval["field_weighted"]["percentage"],
        "DLI_min": crop_eval["DLI_min"],
        "DLI_opt": crop_eval["DLI_opt"],
        "unit": crop_eval["unit"],

        # Uniformità luce
        "light_uniformity": uniformity,
    }