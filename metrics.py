"""
Modulo per la generazione e visualizzazione delle card metriche
Funzionalità:
- Creazione card metriche individuali
- Layout responsivo (3 card per riga su desktop, 1 su mobile)
- Formattazione valori con unità di misura
- Visualizzazione W/m² e Wh/m² per GHI, DNI e POA
"""

import streamlit as st

# ==================== UTILITY ====================

def get_screen_width() -> int:
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return 1200

def format_value(value: float, unit: str = "", decimals: int = 0) -> str:
    return f"{value:.{decimals}f} {unit}".strip()

def create_metric_card(label: str, value: str, description: str, color: str = None) -> str:
    color_style = f"color:{color};" if color else ""
    return f"""
    <div class="metric-card" style="
        background:#f0f2f6;
        padding:1rem;
        margin:0.25rem;
        border-radius:0.5rem;
        text-align:center;
    ">
        <div class="metric-label" style="font-weight:600; font-size:0.9rem;">
            {label}
        </div>
        <div class="metric-value" style="font-size:1.2rem; margin:0.2rem 0; {color_style}">
            {value}
        </div>
        <div class="metric-description" style="font-size:0.75rem; color:#555;">
            {description}
        </div>
    </div>
    """

# ==================== GENERAZIONE METRICHE ====================

def generate_solar_metrics(results: dict) -> list:
    """
    Genera metriche di irradianza solare in W/m² (medio orario) e Wh/m² (cumulativo giornaliero)
    """
    ghi_w = results['GHI_Wm2'].mean()
    dni_w = results['DNI_Wm2'].mean()
    poa_w = results['POA_Wm2'].mean()
    
    ghi_wh = results['GHI_Whm2']
    dni_wh = results['DNI_Whm2']
    poa_wh = results['POA_Whm2']
    
    return [
    create_metric_card(
        "GHI",
        f"{format_value(ghi_w, 'W/m²')}<br>{format_value(ghi_wh, 'Wh/m²')}",
        "Radiazione globale orizzontale: media oraria e totale giornaliera."
    ),
    create_metric_card(
        "DNI",
        f"{format_value(dni_w, 'W/m²')}<br>{format_value(dni_wh, 'Wh/m²')}",
        "Radiazione diretta normale: media oraria e totale giornaliera."
    ),
    create_metric_card(
        "POA",
        f"{format_value(poa_w, 'W/m²')}<br>{format_value(poa_wh, 'Wh/m²')}",
        "Radiazione sul piano dei pannelli: media oraria e totale giornaliera."
    ),
    ]   



def generate_geometric_metrics(results: dict) -> list:
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
            "Land Area Coverage (GCR)",
            format_value(gcr * 100, "%", decimals=1),
            "Rapporto tra superficie pannelli e area totale del sito.",
            color=gcr_color
        ),
    ]

def generate_metric_cards(params: dict, results: dict) -> list:
    solar_cards = generate_solar_metrics(results)
    geometric_cards = generate_geometric_metrics(results)
    return solar_cards + geometric_cards

# ==================== LAYOUT ====================

def display_metrics_grid(metric_cards: list, cards_per_row: int = 3):
    for i in range(0, len(metric_cards), cards_per_row):
        row_cards = metric_cards[i:i + cards_per_row]
        while len(row_cards) < cards_per_row:
            row_cards.append("")
        cols = st.columns(cards_per_row, gap="medium")
        for col, card_html in zip(cols, row_cards):
            if card_html:
                col.markdown(card_html, unsafe_allow_html=True)

def display_metrics_single_column(metric_cards: list):
    for card in metric_cards:
        st.markdown(card, unsafe_allow_html=True)

def display_metrics(params: dict, results: dict):
    st.markdown('<p class="section-header">OUTPUT</p>', unsafe_allow_html=True)
    metric_cards = generate_metric_cards(params, results)
    
    screen_width = get_screen_width()
    if screen_width > 768:
        display_metrics_grid(metric_cards, cards_per_row=3)
    else:
        display_metrics_single_column(metric_cards)
