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
    
    # Calcola alcuni indicatori aggiuntivi
    efficienza_sistema = (results['E_day'] / (results['poa']['poa_global'].sum()/1000 * results['gcr'] * 10000)) * 100 if results['poa']['poa_global'].sum() > 0 else 0
    rapporto_energetico = results['E_suolo_tot_ha'] / results['clearsky']['ghi'].sum()/1000 * 100 if results['clearsky']['ghi'].sum() > 0 else 0
    
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
            f"{results['P_ac'].max():.2f} kW",
            "Potenza massima istantanea dei pannelli."
        ),
        create_metric_card(
            "⚡ POA Totale",
            f"{results['poa']['poa_global'].sum()/1000:.2f} kWh/m²",
            "Radiazione sul piano dei pannelli (tilt/azimuth)."
        ),
        create_metric_card(
            "⚡ Energia Giornaliera Pannelli",
            f"{results['E_day']:.0f} kWh/ha",
            "Energia elettrica generata dai pannelli (giornaliera)."
        ),
        create_metric_card(
            "⚡ Efficienza Sistema",
            f"{efficienza_sistema:.1f} %",
            "Rendimento complessivo del sistema (energia prodotta/radiazione POA)."
        ),
        
        # 📐 Parametri geometrici
        create_metric_card(
            "📐 Superficie Totale Pannelli",
            f"{params['num_panels']*params['area']:.0f} m²",
            "Area totale occupata dai pannelli installati."
        ),
        create_metric_card(
            "📐 Land Area Coverage (GCR)",
            f"{results['gcr']*100:.1f} %",
            "Rapporto tra superficie pannelli e area totale sito.",
            color="red" if results['gcr']*100 > 40 else "green"
        ),

        # 🌱 Agro-FV - NUOVE CARD
        create_metric_card(
            "🌱 Radiazione Suolo (per ettaro)",
            f"{results['E_suolo_tot_ha']:.0f} kWh/ha",
            "Radiazione TOTALE che raggiunge il suolo sull'intero ettaro."
        ),
        create_metric_card(
            "🌱 Radiazione Suolo (per m²)",
            f"{results['E_suolo'].sum()/1000:.1f} kWh/m²",
            "Radiazione media sul terreno illuminato tra i pannelli."
        ),
        create_metric_card(
            "🌱 Frazione Suolo Illuminato Medio",
            f"{results['f_luce'].mean()*100:.1f} %",
            "Percentuale media di terreno non ombreggiato durante il giorno."
        ),
        create_metric_card(
            "🌱 Rapporto Radiazione Suolo/GHI",
            f"{rapporto_energetico:.1f} %",
            "Percentuale di radiazione che raggiunge il suolo rispetto al GHI totale.",
            color="orange" if rapporto_energetico < 50 else "green"
        ),
        create_metric_card(
            "🌱 Ore di Luce Solare Utile",
            f"{(results['f_luce'] > 0.1).sum():.0f} h",
            "Numero di ore con illuminazione significativa del suolo (>10%)."
        ),
        create_metric_card(
            "🌱 Picco Illuminazione Suolo",
            f"{results['f_luce'].max()*100:.0f} %",
            "Massima frazione di luce che raggiunge il suolo durante il giorno."
        )
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

def display_energy_comparison(results):
    """Visualizza un confronto diretto tra energia prodotta e radiazione al suolo"""
    
    st.markdown("---")
    st.markdown("### 📊 Confronto Energetico per Ettaro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌞 Energia Solare Totale",
            value=f"{results['clearsky']['ghi'].sum()/1000 * 10000:.0f} kWh/ha",
            help="Radiazione che arriverebbe sull'ettaro senza pannelli"
        )
    
    with col2:
        st.metric(
            label="⚡ Energia Prodotta Pannelli",
            value=f"{results['E_day']:.0f} kWh/ha",
            help="Energia elettrica generata dai pannelli"
        )
    
    with col3:
        st.metric(
            label="🌱 Energia che Raggiunge il Suolo",
            value=f"{results['E_suolo_tot_ha']:.0f} kWh/ha",
            help="Radiazione disponibile per le coltivazioni sotto i pannelli"
        )
    
    # Calcolo efficienza di utilizzo del terreno
    energia_totale_utilizzata = results['E_day'] + results['E_suolo_tot_ha']
    energia_solare_totale = results['clearsky']['ghi'].sum()/1000 * 10000
    
    if energia_solare_totale > 0:
        efficienza_terreno = (energia_totale_utilizzata / energia_solare_totale) * 100
        
        st.info(f"""
        **Efficienza di utilizzo del terreno: {efficienza_terreno:.1f}%**
        
        - ⚡ Energia elettrica prodotta: **{results['E_day']:.0f} kWh/ha** ({results['E_day']/energia_totale_utilizzata*100:.1f}%)
        - 🌱 Energia per coltivazioni: **{results['E_suolo_tot_ha']:.0f} kWh/ha** ({results['E_suolo_tot_ha']/energia_totale_utilizzata*100:.1f}%)
        
        *L'Agro-FV permette di utilizzare contemporaneamente la radiazione solare per produzione energetica e agricola.*
        """)

# Nel tuo main app, dopo display_metrics, aggiungi:
# display_energy_comparison(results)    