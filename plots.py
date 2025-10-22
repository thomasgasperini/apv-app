# plots.py
"""
Modulo per la generazione dei grafici
- Grafico potenza AC
- Grafico irradianza
"""

import streamlit as st
import matplotlib.pyplot as plt
from config import CHART_CONFIG, COLORS


def get_screen_width():
    """Rileva larghezza schermo"""
    try:
        from screeninfo import get_monitors
        return get_monitors()[0].width
    except:
        return CHART_CONFIG["screen_width_fallback"]


def plot_power_graph(ax, times, P_ac, comune, data):
    """Grafico potenza AC"""
    ax.fill_between(times, P_ac, alpha=0.3, color=COLORS["primary"])
    ax.plot(times, P_ac, linewidth=2.5, color=COLORS["primary"], label='⚡ Potenza AC Pannelli')
    ax.set_xlabel('Ora del giorno')
    ax.set_ylabel('Potenza [W]')
    ax.set_title(f'Produzione Elettrica - {comune} ({data})')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()
    
    # Imposta tick sull'asse x
    step = max(1, len(times)//8)
    ax.set_xticks(times[::step])
    ax.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)


def plot_irradiance_graph(ax, times, clearsky, poa, E_suolo):
    """Grafico irradianza"""
    ax.plot(times, clearsky['ghi'], label='🌞 GHI Orizzontale', 
            color=COLORS["warning"], linewidth=1.5)
    ax.plot(times, clearsky['dni'], label='🌞 DNI Diretta', 
            color=COLORS["danger"], linewidth=1.5)
    ax.plot(times, poa['poa_global'], label='⚡ POA sul Pannello', 
            color=COLORS["primary"], linewidth=1.5)
    
    if E_suolo is not None:
        ax.plot(times, E_suolo, label='🌱 Radiazione suolo', 
                color=COLORS["info"], linestyle='--', linewidth=2)
    
    ax.set_xlabel('Ora del giorno')
    ax.set_ylabel('Irradianza [W/m²]')
    ax.set_title('Irradianza Solare e Agro-FV')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()
    
    # Imposta tick sull'asse x
    step = max(1, len(times)//8)
    ax.set_xticks(times[::step])
    ax.set_xticklabels([t.strftime("%H:%M") for t in times[::step]], rotation=45)


def display_charts(params, results):
    """Visualizza i grafici di produzione e irradianza"""
    
    st.markdown('<p class="section-header">📈 Analisi Dettagliata</p>', unsafe_allow_html=True)
    
    # Estrazione dati
    times = results["times"]
    P_ac = results["P_ac"]
    poa = results["poa"]
    clearsky = results["clearsky"]
    E_suolo = results.get("E_suolo")
    comune = params["comune"]
    data = params["data"]
    
    # Dimensioni grafici responsive
    screen_width = get_screen_width()
    fig_width = max(CHART_CONFIG["fig_width_min"], 
                    min(CHART_CONFIG["fig_width_max"], screen_width / 100))
    fig_height = CHART_CONFIG["fig_height"]
    
    # Creazione figura con 2 subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height), 
                                     constrained_layout=True)
    
    # Grafico potenza
    plot_power_graph(ax1, times, P_ac, comune, data)
    
    # Grafico irradianza
    plot_irradiance_graph(ax2, times, clearsky, poa, E_suolo)
    
    # Visualizza in Streamlit
    st.pyplot(fig, use_container_width=True)