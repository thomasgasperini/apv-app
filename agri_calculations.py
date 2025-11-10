"""
Modulo Calcoli Agricoli - Parametri agrivoltaico (microclima rimosso)
Analizza l'impatto dei pannelli FV sulle colture sottostanti tramite DLI
"""
# sito enea per DLI mensile italiano: https://www.solaritaly.enea.it/DLI/DLIMappeEn.php#:~:text=Maps%20of%20Daily%20Light%20Integral%20in%20Italy.,moles%20per%20square%20meter%20per%20day:%20mol/(m%C2%B2%C2%B7d).
import pandas as pd
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
        "Ortaggi a foglia": {"DLI_min": 12, "DLI_opt": 20, "unit": "mol/m²/d"},
        "Tuberi": {"DLI_min": 15, "DLI_opt": 20, "unit": "mol/m²/d"},
        "Ortaggi da frutto bassi": {"DLI_min": 20, "DLI_opt": 30, "unit": "mol/m²/d"},
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

        L_shadow = H / math.tan(elev_rad)
        W_shadow = (area_pannello * math.cos(tilt_rad)) / max(L_shadow, 1e-6)
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


def calculate_shaded_fraction(shadow_df: pd.DataFrame, num_panels: int, superficie_campo: float, pitch: float) -> pd.Series:

    effective_shadow_area = []

    for L_shadow, A_shadow in zip(shadow_df['shadow_length_m'], shadow_df['shadow_area_m2']):
        if L_shadow <= pitch or L_shadow == 0:
            # Nessuna sovrapposizione
            A_eff = A_shadow * num_panels
        else:
            # Riduzione proporzionale per sovrapposizione
            overlap_factor = pitch / L_shadow
            A_eff = A_shadow * num_panels * overlap_factor
        
        effective_shadow_area.append(A_eff)
    
    shaded_fraction = pd.Series(effective_shadow_area, index=shadow_df.index) / superficie_campo
    return shaded_fraction.clip(upper=1.0)


# ==================== DLI ====================

def calculate_dli(ghi: pd.Series, shaded_fraction: pd.Series,
                  transmission_under: float = TRANSMISSION_COEFF["under_panel"]) -> pd.Series:
    """
    Calcola il DLI giornaliero in mol/m²/d considerando la frazione di ombra
    """
    # PAR disponibile
    par_total = ghi * PAR_FRACTION
    par_weighted = par_total * (shaded_fraction * transmission_under + (1 - shaded_fraction) * 1.0)

    # Conversione da W/m² a µmol/m²/s: fattore medio 4.6
    par_umol = par_weighted * 4.6

    # DLI giornaliero (µmol/m²/s → mol/m²/d)
    dli_mol = (par_umol.sum() * 3600) / 1e6

    return dli_mol

def evaluate_crop_suitability(dli_value: float, crop_name: str) -> dict:
    """
    Valuta lo stato della coltura in base al DLI giornaliero
    """
    # Recupero requisiti coltura
    requirement_data = None
    for category, crops in DLI_REQUIREMENTS.items():
        if crop_name in crops:
            requirement_data = crops[crop_name]
            break

    if requirement_data is None:
        import streamlit as st
        st.warning(f"⚠️ Crop '{crop_name}' non trovato in DLI_REQUIREMENTS. Uso valori di default.")
        DLI_min, DLI_opt = 80, 100
        unit = "mol/m²/d"
    else:
        DLI_min = requirement_data["DLI_min"]
        DLI_opt = requirement_data["DLI_opt"]
        unit = requirement_data["unit"]

    # Stato coltura
    percentage = (dli_value / DLI_opt) * 100
    if percentage >= 100:
        status, color = "Ottimale", "green"
    elif percentage >= 80:
        status, color = "Adeguato", "orange"
    elif percentage >= 60:
        status, color = "Marginale", "darkorange"
    else:
        status, color = "Insufficiente", "red"

    return {
        "DLI": dli_value,
        "percentage": percentage,
        "status": status,
        "color": color,
        "DLI_min": DLI_min,
        "DLI_opt": DLI_opt,
        "unit": unit
    }

# ==================== FUNZIONE PRINCIPALE ====================

def calculate_all_agri(params: dict, pv_results: dict) -> dict:

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
        shadow_df, 
        params['num_panels_total'], 
        superficie_campo,
        params.get('pitch_laterale', 1.0)  # usa il pitch definito nel sidebar
    )

    # Calcolo DLI giornaliero
    dli_value = calculate_dli(ghi, shaded_fraction)

    # Valutazione coltura
    crop_eval = evaluate_crop_suitability(dli_value, params.get("crops", "Cereali"))

    return {
        "times": pv_results['times'],
        "shaded_fraction": shaded_fraction,
        "shadow_length_m": shadow_df['shadow_length_m'],
        "shadow_area_m2": shadow_df['shadow_area_m2'],
        "shaded_fraction_avg": shaded_fraction.mean(),
        "shadow_area_max_m2": shadow_df['shadow_area_m2'].max(),
        "shadow_length_max_m": shadow_df['shadow_length_m'].max(),
        "DLI_mol_m2_day": crop_eval["DLI"],
        "crop_status": crop_eval["status"],
        "crop_status_color": crop_eval["color"],
        "crop_light_adequacy_pct": crop_eval["percentage"],
        "DLI_min": crop_eval["DLI_min"],
        "DLI_opt": crop_eval["DLI_opt"],
        "unit": crop_eval["unit"]
    }
