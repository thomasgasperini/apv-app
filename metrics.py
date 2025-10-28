"""
Modulo per visualizzazione metriche PV
Funzionalità:
- Creazione card metriche W/m², Wh/m², W e Wh
- Layout responsivo
- Visualizzazione GHI, DNI, DHI, POA globale e produzione elettrica
- Visualizzazione metriche geometriche: superficie, GCR e spazio vuoto
"""

import streamlit as st
from calculations import calculate_empty_space_per_hectare

# ==================== UTILITY ====================

def get_screen_width() -> int:
    """Ritorna la larghezza dello schermo, fallback a 1200 px."""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return 1200

def format_value(value: float, unit: str = "", decimals: int = 0) -> str:
    """Formatta un valore numerico con unità e decimali."""
    return f"{value:.{decimals}f} {unit}".strip()

def create_metric_card(label: str, value: str, description: str, color: str = None) -> str:
    """Crea una card HTML per visualizzare una metrica."""
    color_style = f"color:{color};" if color else ""
    return f"""
    <div class="metric-card" style="
        background:#f0f2f6;
        padding:1rem;
        margin:0.25rem;
        border-radius:0.5rem;
        text-align:center;
    ">
        <div class="metric-label" style="font-weight:600; font-size:0.9rem;">{label}</div>
        <div class="metric-value" style="font-size:1.2rem; margin:0.2rem 0; {color_style}">{value}</div>
        <div class="metric-description" style="font-size:0.75rem; color:#555;">{description}</div>
    </div>
    """

# ==================== METRICHE SOLARI ====================

def generate_solar_metrics(results: dict) -> list:
    """Genera metriche radiazione e produzione elettrica."""
    return [
        create_metric_card(
            "GHI",
            f"{format_value(results['GHI_Wm2'].mean(), 'W/m²')}<br>{format_value(results['GHI_Whm2'], 'Wh/m²')}",
            "Radiazione globale orizzontale: media oraria e totale giornaliera."
        ),
        create_metric_card(
            "DNI",
            f"{format_value(results['DNI_Wm2'].mean(), 'W/m²')}<br>{format_value(results['DNI_Whm2'], 'Wh/m²')}",
            "Radiazione diretta normale: media oraria e totale giornaliera."
        ),
        create_metric_card(
            "DHI",
            f"{format_value(results['DHI_Wm2'].mean(), 'W/m²')}<br>{format_value(results['DHI_Whm2'], 'Wh/m²')}",
            "Radiazione diffusa orizzontale: media oraria e totale giornaliera."
        ),
        create_metric_card(
            "POA",
            f"{format_value(results['POA_global_Wm2'].mean(), 'W/m²')}<br>{format_value(results['POA_Whm2'], 'Wh/m²')}",
            "Radiazione sul piano dei pannelli: media oraria e totale giornaliera."
        ),
        create_metric_card(
            "Produzione Elettrica",
            f"{format_value(results['PV_power_W'].mean(), 'W')}<br>{format_value(results['PV_energy_Wh'], 'Wh')}",
            "Produzione elettrica media oraria e totale giornaliera."
        )
    ]

# ==================== METRICHE GEOMETRICHE ====================

def generate_geometric_metrics(results: dict, params: dict) -> list:
    """Genera metriche geometriche: superficie, GCR, spazio vuoto e dimensioni impianto."""
    
    # Calcola lo spazio vuoto e dimensioni totali
    empty_space = calculate_empty_space_per_hectare(
        base_pannello=params["base_pannello"],
        altezza_pannello=params["altezza_pannello"],
        tilt=params["tilt_pannello"],
        pitch_laterale=params["pitch_laterale"],
        pitch_verticale=params["pitch_verticale"],
        pannelli_per_fila=params["pannelli_per_fila"],
        num_file=params["num_file"]
    )
    
    superficie = results['superficie_effettiva']
    gcr = results['gcr']
    gcr_color = "red" if gcr > 0.4 else "green"

    return [
        create_metric_card(
            "Superficie Totale Pannelli",
            format_value(superficie, "m²", decimals=0),
            "Area complessiva dei pannelli installati."
        ),
        create_metric_card(
            "Suolo Occupato da Pannelli",
            format_value(empty_space["superficie_occupata"], "m²", decimals=1),
            "Superficie effettivamente coperta dai pannelli (tiene conto della proiezione).",
        ),
        create_metric_card(
            "Land Area Coverage (GCR)",
            format_value(gcr * 100, "%", decimals=1),
            "Rapporto tra superficie pannelli e area totale del sito.",
            color=gcr_color
        ),
        create_metric_card(
            "Superficie Libera nel Sito",
            format_value(empty_space["superficie_vuota"], "m²", decimals=1),
            "Superficie del sito non occupata dai pannelli.",
        )
    ]

# ==================== GENERAZIONE TUTTE LE METRICHE ====================

def generate_metric_cards(results: dict, params: dict) -> list:
    """Genera tutte le metriche combinate."""
    return generate_solar_metrics(results) + generate_geometric_metrics(results, params)

# ==================== DISPLAY METRICHE ====================

def display_metrics(results: dict, params: dict):
    """Visualizza le metriche in Streamlit con layout responsivo."""

    # --- Titolo metriche solari ---
    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">Parametri di irradiamento solare e produzione energetica</p>',
        unsafe_allow_html=True
    )

    metric_cards_solar = generate_solar_metrics(results)
    display_card_group(metric_cards_solar)

    # --- Titolo metriche geometriche ---
    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">Geometria e copertura dei moduli</p>',
        unsafe_allow_html=True
    )

    metric_cards_geom = generate_geometric_metrics(results, params)
    display_card_group(metric_cards_geom)

def display_card_group(cards: list):
    """Funzione helper per disporre le card con layout responsivo."""
    screen_width = get_screen_width()
    if screen_width > 768:
        for i in range(0, len(cards), 3):
            row_cards = cards[i:i+3]
            while len(row_cards) < 3:
                row_cards.append("")
            cols = st.columns(3, gap="medium")
            for col, card in zip(cols, row_cards):
                if card:
                    col.markdown(card, unsafe_allow_html=True)
    else:
        for card in cards:
            st.markdown(card, unsafe_allow_html=True)
