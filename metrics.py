"""
Modulo Metriche - Visualizzazione risultati con card pulite e moderne
"""

import streamlit as st


# ==================== UTILITY ====================

def format_value(value: float, unit: str = "", decimals: int = 0) -> str:
    """Formatta valore con unità"""
    return f"{value:.{decimals}f} {unit}".strip()


def create_metric_card(label: str, value: str, description: str = "", color: str = None) -> str:
    """
    Crea card HTML per metrica
    
    Args:
        label: titolo metrica
        value: valore (può includere HTML come <br>)
        description: descrizione opzionale
        color: colore valore opzionale
    
    Returns:
        HTML card
    """
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
        {f'<div class="metric-description" style="font-size:0.75rem; color:#555;">{description}</div>' if description else ''}
    </div>
    """


def get_screen_width() -> int:
    """Rileva larghezza schermo (fallback: 1200px)"""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return 1200


def display_card_group(cards: list):
    """
    Dispone card in layout responsivo
    
    Desktop: 3 card per riga
    Mobile: 1 card per riga
    """
    screen_width = get_screen_width()
    
    if screen_width > 768:
        # Layout desktop: 3 colonne
        for i in range(0, len(cards), 3):
            row_cards = cards[i:i+3]
            while len(row_cards) < 3:
                row_cards.append("")
            
            cols = st.columns(3, gap="medium")
            for col, card in zip(cols, row_cards):
                if card:
                    col.markdown(card, unsafe_allow_html=True)
    else:
        # Layout mobile: 1 colonna
        for card in cards:
            st.markdown(card, unsafe_allow_html=True)


# ==================== GENERAZIONE METRICHE ====================

def generate_solar_metrics(results: dict) -> list:
    """
    Genera card per metriche solari
    
    Returns:
        Lista di card HTML
    """
    return [
        create_metric_card(
            "GHI",
            f"{format_value(results['GHI_Wm2'].mean(), 'W/m²')}<br>"
            f"{format_value(results['GHI_Whm2'], 'Wh/m²')}",
            "Radiazione globale orizzontale (media oraria / totale giornaliero)"
        ),
        
        create_metric_card(
            "DNI",
            f"{format_value(results['DNI_Wm2'].mean(), 'W/m²')}<br>"
            f"{format_value(results['DNI_Whm2'], 'Wh/m²')}",
            "Radiazione diretta normale (media oraria / totale giornaliero)"
        ),
        
        create_metric_card(
            "DHI",
            f"{format_value(results['DHI_Wm2'].mean(), 'W/m²')}<br>"
            f"{format_value(results['DHI_Whm2'], 'Wh/m²')}",
            "Radiazione diffusa orizzontale (media oraria / totale giornaliero)"
        ),
        
        create_metric_card(
            "POA",
            f"{format_value(results['POA_Wm2'].mean(), 'W/m²')}<br>"
            f"{format_value(results['POA_Whm2'], 'Wh/m²')}",
            "Radiazione sul piano pannelli (media oraria / totale giornaliero)"
        ),
        
        create_metric_card(
            "T° Media Celle",
            f"{format_value(results['T_cell_avg'], '°C', 1)}",
            "Temperatura media delle celle fotovoltaiche"
        ),
    ]


def generate_production_metrics(results: dict) -> list:
    """
    Genera card per produzione elettrica
    
    Returns:
        Lista di card HTML
    """
    return [
        create_metric_card(
            "Produzione Singolo Pannello",
            f"{format_value(results['power_single_W'].mean(), 'W')}<br>"
            f"{format_value(results['energy_single_Wh'], 'Wh')}",
            "Potenza media oraria / Energia giornaliera singolo pannello"
        ),
        
        create_metric_card(
            "Produzione Totale",
            f"{format_value(results['power_total_W'].mean(), 'W')}<br>"
            f"{format_value(results['energy_total_Wh'], 'Wh')}",
            "Potenza media oraria / Energia giornaliera tutti i pannelli"
        ),
        
        create_metric_card(
            "Produzione Energetica per m²",
            f"{format_value(results['energy_total_Wh_m2'], 'Wh/m²', 1)}",
            "Energia giornaliera per metro quadro di pannello"
        ),
    ]

def generate_geometric_metrics(results: dict) -> list:
    """
    Genera card per metriche geometriche
    
    Returns:
        Lista di card HTML
    """
    gcr = results['gcr']
    gcr_color = "red" if gcr > 0.4 else "green"
    
    return [
        create_metric_card(
            "Superficie Totale Pannelli",
            f"{format_value(results['superficie_totale_pannelli'], 'm²', 0)}",
            "Area nominale totale (base × altezza × numero pannelli)"
        ),
        
        create_metric_card(
            "Spazio Occupato (Proiezione)",
            f"{format_value(results['proiezione_totale_pannelli'], 'm²', 0)}",
            "Ingombro al suolo considerando tilt (proiezione pannelli)"
        ),

        create_metric_card(
            "GCR (Ground Coverage Ratio)",
            f"{format_value(gcr * 100, '%', 1)}",
            "Rapporto tra proiezione pannelli e superficie campo",
            color=gcr_color
        ),
        
        create_metric_card(
            "Superficie Libera",
            f"{format_value(results['superficie_libera'], 'm²', 0)}",
            "Terreno libero disponibile (campo - proiezione pannelli)"
        ),

        create_metric_card(
            "Pannelli installabili",
            f"{format_value(results['total_panels'], '', 0)}",
            "N. pannelli installabili secondo dimensionamento (campo/pannelli)"
        )
    ]

def generate_agri_metrics(agri_results: dict) -> list:
    """
    Genera card per metriche agrivoltaiche semplificate
    """

    crop_color = agri_results.get('crop_status_color', None)

    return [
        create_metric_card(
            "DLI totale giornaliero",
            f"{format_value(agri_results['DLI_mol_m2_day'], 'mol/m²·day', 1)}",
            "Totale giornaliero di luce fotosinteticamente attiva"
        ),

        create_metric_card( 
            "DLI Richiesto",
            f"{format_value(agri_results['DLI_min'], agri_results['unit'])}<br>"
            f"{format_value(agri_results['DLI_opt'], agri_results['unit'])}",
            "Fabbisogno giornaliero della coltura (min - ottimale)"
        ),

        create_metric_card(
            "Adeguatezza Luminosità",
            f"{format_value(agri_results['crop_light_adequacy_pct'], '%', 0)}",
            "Percentuale del fabbisogno luminoso soddisfatto dalla luce disponibile",
            color=crop_color
        ),

        create_metric_card(
            "Stato Coltura",
            agri_results['crop_status'],
            "Valutazione dell'idoneità agronomica della coltura secondo il DLI",
            color=crop_color
        ),

        create_metric_card(
            "Ombreggiamento Medio",
            f"{format_value(agri_results['shaded_fraction_avg']*100, '%', 1)}",
            "Media giornaliera della frazione di superficie del campo in ombra"
        ),
        
        create_metric_card(
            "Ombra Massima",
            f"{format_value(agri_results['shadow_area_max_m2'], 'm²', 0)}",
            "Area massima in ombra rilevata sul campo durante la giornata"
        ),
    ]



# ==================== FUNZIONE PRINCIPALE ====================

def display_metrics(results: dict, params: dict):
    """
    Visualizza tutte le metriche organizzate in sezioni
    
    Args:
        results: dizionario risultati da calculate_all_pv()
        params: parametri input
    """
    # SEZIONE 1: Irradiamento Solare
    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">'
        'Irradiamento Solare e Temperatura Pannelli'
        '</p>',
        unsafe_allow_html=True
    )
    solar_cards = generate_solar_metrics(results)
    display_card_group(solar_cards)
    
    # SEZIONE 2: Produzione Elettrica
    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">'
        'Produzione Elettrica'
        '</p>',
        unsafe_allow_html=True
    )
    production_cards = generate_production_metrics(results)
    display_card_group(production_cards)
    
    # SEZIONE 3: Copertura Terreno e Dimensionamento
    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">'
        'Geometria e Copertura Terreno'
        '</p>',
        unsafe_allow_html=True
    )
    geometric_cards = generate_geometric_metrics(results)
    display_card_group(geometric_cards)

    # SEZIONE 4: Metriche Agrivoltaiche

    st.markdown(
        '<p class="section-header" style="margin-top: 1rem;">'
        'Metriche Agronomiche'
        '</p>',
        unsafe_allow_html=True
        )
    agri_cards = generate_agri_metrics(results["agri_results"])
    display_card_group(agri_cards)

