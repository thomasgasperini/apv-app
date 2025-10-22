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


def create_metric_card(label, value, description):
    """Crea una singola card metrica"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """


def generate_metric_cards(params, results):
    """Genera tutte le card metriche"""
    
    clearsky = results["clearsky"]
    poa = results["poa"]
    P_ac = results["P_ac"]
    superficie_effettiva = params['num_panels'] * params['pitch_laterale'] * params['pitch_file']
    
    metric_cards = [
        # 🌞 Energia solare incidente
        create_metric_card(
            "🌞 GHI Totale",
            f"{clearsky['ghi'].sum()/1000:.2f} kWh/m²",
            "Radiazione globale orizzontale sul sito, senza pannelli."
        ),
        create_metric_card(
            "🌞 DNI Totale",
            f"{clearsky['dni'].sum()/1000:.2f} kWh/m²",
            "Radiazione diretta dal sole perpendicolare ai raggi."
        ),
        
        # ⚡ Energia prodotta dai pannelli
        create_metric_card(
            "⚡ Energia Giornaliera Pannelli",
            f"{results['E_day']:.2f} kWh/ha",
            "Energia elettrica generata dai pannelli (giornaliera)."
        ),
        create_metric_card(
            "⚡ Picco Potenza AC",
            f"{P_ac.max():.0f} W",
            "Potenza massima istantanea dei pannelli."
        ),
        create_metric_card(
            "⚡ POA Totale",
            f"{poa['poa_global'].sum()/1000:.2f} kWh/m²",
            "Radiazione sul piano dei pannelli (tilt/azimuth)."
        ),
        
        # 🌱 Agro-FV
        create_metric_card(
            "🌱 Energia suolo tra pannelli",
            f"{results['E_suolo_tot']:.2f} kWh/ha",
            "Radiazione che raggiunge il terreno tra i pannelli."
        ),
        create_metric_card(
            "🌱 Frazione suolo illuminata",
            f"{results['f_luce']*100:.1f} %",
            "Percentuale di terreno non ombreggiato dai pannelli."
        ),
        
        # 📐 Parametri geometrici
        create_metric_card(
            "📐 Area Totale Pannelli",
            f"{params['num_panels']*params['area']:.0f} m²",
            "Superficie fisica dei pannelli installati."
        ),
        create_metric_card(
            "📐 Superficie Effettiva Occupata",
            f"{superficie_effettiva:.0f} m²",
            "Area complessiva inclusi spazi tra file."
        ),
        create_metric_card(
            "📐 Land Area Occupation Ratio",
            f"{results['fattore_copertura']*100:.1f} %",
            "Rapporto tra pannelli e area totale del sito."
        ),
        create_metric_card(
            "📐 Pitch (Laterale / File)",
            f"{params['pitch_laterale']:.2f} m / {params['pitch_file']:.2f} m",
            "Distanza tra pannelli e tra file."
        ),
        create_metric_card(
            "📐 Tilt / Azimuth",
            f"{params['tilt']}° / {params['azimuth']}°",
            "Inclinazione e orientamento dei pannelli."
        ),
        create_metric_card(
            "📐 Albedo / Perdite",
            f"{params['albedo']:.2f} / {params['losses']*100:.1f} %",
            "Riflettanza del terreno e perdite complessive impianto."
        ),
    ]
    
    return metric_cards


def display_metrics(params, results):
    """Visualizza le metriche con layout responsivo"""
    
    st.markdown('<p class="section-header">⚡ Risultati Produzione & Agro-FV</p>', unsafe_allow_html=True)
    
    metric_cards = generate_metric_cards(params, results)
    screen_width = get_screen_width()
    
    # Layout responsivo
    if screen_width > 1200:
        cols = st.columns(5, gap="medium")
        for i, card in enumerate(metric_cards):
            cols[i % 5].markdown(card, unsafe_allow_html=True)
    elif screen_width > 768:
        cols = st.columns(2, gap="medium")
        for i in range(0, len(metric_cards), 2):
            for c, card in zip(cols, metric_cards[i:i+2]):
                c.markdown(card, unsafe_allow_html=True)
    else:
        for card in metric_cards:
            st.markdown(card, unsafe_allow_html=True)
