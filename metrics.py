# metrics.py
"""
Modulo per la generazione delle card metriche
- Risultati energetici
- Parametri geometrici
- Indicatori Agro-FV
"""

import streamlit as st

def get_screen_width():
    """Rileva larghezza schermo per layout responsivo"""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return 1200  # fallback

def create_metric_card(label, value, description, color=None):
    """Crea una singola card metrica con colore opzionale"""
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

def generate_metric_cards(params, results):
    """Genera tutte le card metriche"""
    
    metric_cards = [
        # 🌞 Energia solare incidente
        create_metric_card(
            "🌞 GHI Totale",
            f"{results['clearsky']['ghi'].sum()/1000:.2f} kWh/m²",
            "Radiazione globale orizzontale sul sito, senza pannelli."
        ),
        create_metric_card(
            "🌞 DNI Totale",
            f"{results['clearsky']['dni'].sum()/1000:.2f} kWh/m²",
            "Radiazione diretta perpendicolare ai raggi solari."
        ),
        
        # ⚡ Energia prodotta dai pannelli
        create_metric_card(
            "⚡ Picco Potenza AC",
            f"{results['P_ac'].max():.0f} W",
            "Potenza massima istantanea dei pannelli."
        ),
        create_metric_card(
            "⚡ POA Totale",
            f"{results['poa']['poa_global'].sum()/1000:.2f} kWh/m²",
            "Radiazione sul piano dei pannelli (tilt/azimuth)."
        ),
        create_metric_card(
            "⚡ Energia Giornaliera Pannelli",
            f"{results['E_day']:.2f} kWh/ha",
            "Energia elettrica generata dai pannelli (giornaliera)."
        ),
        
        # 📐 Parametri geometrici
        create_metric_card(
            "📐 Superficie Totale dei Pannelli",
            f"{params['num_panels']*params['area']:.0f} m²",
            "Area totale occupata dai pannelli installati."
        ),
        create_metric_card(
            "📐 Land Area Coverage (GCR)",
            f"{results['gcr']*100:.2f} %",
            "Rapporto tra superficie pannelli e area totale sito.",
            color="red" if results['gcr']*100 > 40 else None
        ),

        # 🌱 Agro-FV
        create_metric_card(
            "🌱 Radiazione suolo",
            f"{results['E_suolo_tot']:.2f} kWh/m²",
            "Radiazione che raggiunge il terreno tra i pannelli."
        ),
        create_metric_card(
            "🌱 Frazione suolo illuminata",
            f"{results['f_luce']*100:.1f} %",
            "Percentuale di terreno non ombreggiato dai pannelli."
        ),
    ]
    return metric_cards

def display_metrics(params, results):
    """Visualizza le metriche con layout responsivo a 3 schede per riga"""
    
    st.markdown('<p class="section-header">⚡ Risultati Produzione & Agro-FV</p>', unsafe_allow_html=True)
    
    metric_cards = generate_metric_cards(params, results)
    screen_width = get_screen_width()
    
    cards_per_row = 3

    # Desktop e tablet: 3 schede per riga
    if screen_width > 768:
        for i in range(0, len(metric_cards), cards_per_row):
            row_cards = metric_cards[i:i+cards_per_row]
            # aggiungi card vuote se meno di 3
            row_cards += [""] * (cards_per_row - len(row_cards))
            cols = st.columns(cards_per_row, gap="medium")
            for c, card in zip(cols, row_cards):
                if card:
                    c.markdown(card, unsafe_allow_html=True)

    # Mobile: 1 scheda per riga
    else:
        for card in metric_cards:
            st.markdown(card, unsafe_allow_html=True)

