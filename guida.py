"""
Guida Completa al Simulatore Agrivoltaico RESFARM
Spiega teoria, implementazione e calcoli del simulatore
"""

import streamlit as st


def show_pv_guide():
    """Visualizza guida completa in expander"""
    
    with st.expander("📖 Guida Completa al Simulatore", expanded=False):
        
        # ==================== HEADER ====================
        st.markdown("""
        <div style="text-align:center; padding:1rem; background:linear-gradient(135deg, #74a65b, #a3c68b); border-radius:10px; margin-bottom:2rem;">
            <h1 style="color:white; margin:0;">🌞 Guida Completa</h1>
            <p style="color:white; font-size:1.1rem; margin:0.5rem 0 0 0;">
                Simulatore Agrivoltaico RESFARM
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ==================== INDICE ====================
        st.markdown("## 📋 Indice")
        st.markdown("""
        1. [Introduzione](#introduzione)
        2. [Cosa Calcola il Simulatore](#cosa-calcola)
        3. [Parametri di Input](#parametri-input)
        4. [Fase 1: Calcoli Geometrici](#fase-1-geometria)
        5. [Fase 2: Calcoli Solari](#fase-2-solare)
        6. [Fase 3: Produzione Elettrica](#fase-3-produzione)
        7. [Limitazioni Attuali](#limitazioni)
        """)
        
        st.markdown("---")
        
        # ==================== INTRODUZIONE ====================
        st.markdown("## 🎯 Introduzione")
        st.markdown("""
        Questo simulatore stima la **produzione elettrica giornaliera** di un impianto **agrivoltaico**, analizzando:
        
        - 📐 **Geometria e layout** dei pannelli sul terreno
        - ☀️ **Irraggiamento solare** sulla superficie inclinata
        - ⚡ **Conversione fotovoltaica** considerando temperatura delle celle
        
        Il modello assume **condizioni di cielo sereno** (clearsky) per una singola giornata, 
        fornendo una stima ottimistica della produzione.
        
        > **Nota Importante:** Questa è una simulazione ideale. Le condizioni reali includono 
        > nuvole, sporcizia, ombreggiamenti e altri fattori che riducono la produzione del 20-30%.
        """)
        
        st.markdown("---")
        
        # ==================== COSA CALCOLA ====================
        st.markdown("## 🧮 Cosa Calcola il Simulatore")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 1️⃣ Geometria
            - Superficie totale pannelli
            - Proiezione a terra (con tilt)
            - GCR (copertura terreno)
            - Superficie libera coltivabile
            """)
        
        with col2:
            st.markdown("""
            ### 2️⃣ Irraggiamento
            - GHI, DNI, DHI
            - POA (piano pannelli)
            - Valori orari e giornalieri
            - Temperatura ambiente
            """)
        
        with col3:
            st.markdown("""
            ### 3️⃣ Produzione
            - Potenza oraria [W]
            - Energia giornaliera [Wh]
            - Energia per m²
            - Temperatura celle
            """)
        
        st.markdown("---")
        
        # ==================== PARAMETRI INPUT ====================
        st.markdown("## 🔧 Parametri di Input")
        
        st.markdown("### 📍 Localizzazione")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `comune` | Testo | Geocoding → coordinate GPS |
        | `lat`, `lon` | Numerico [°] | Calcolo posizione sole (`pvlib.solarposition`) |
        | `data` | Data | Serie temporale oraria (`pd.date_range`) |
        | `timezone` | Fuso orario | Conversione tempo solare |
        """)
        
        st.markdown("### 🔲 Layout Pannelli")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `num_panels_per_row` | Intero | Calcolo larghezza layout (`larghezza_totale`) |
        | `num_rows` | Intero | Calcolo profondità layout (`profondita_totale`) |
        | `base_pannello` | Numerico [m] | Area pannello, larghezza totale |
        | `altezza_pannello` | Numerico [m] | Area pannello, proiezione con tilt |
        """)
        
        st.markdown("### 📏 Spaziatura")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `distanza_interfile` | Numerico [m] | Spazio libero tra file di pannelli |
        | `pitch_laterale` | Numerico [m] | Distanza centro-centro pannelli affiancati |
        
        > **Nota:** Questi parametri determinano lo spazio disponibile per coltivazioni e manutenzione.
        """)
        
        st.markdown("### ⚡ Orientamento")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `tilt_pannello` | Numerico [°] | Proiezione (`cos(tilt)`) + POA (`pvlib.irradiance`) |
        | `azimuth_pannello` | Numerico [°] | Calcolo POA (Sud = 180°) |
        """)
        
        st.markdown("### 🔋 Caratteristiche Elettriche")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `eff` | Numerico [%] | Conversione radiazione→potenza |
        | `temp_coeff` | Numerico [%/°C] | Correzione efficienza con temperatura |
        | `noct` | Numerico [°C] | Stima temperatura celle |
        | `losses` | Numerico [%] | Perdite cavi, inverter, sporcizia |
        | `albedo` | Numerico [0-1] | Componente riflessa radiazione |
        """)
        
        st.markdown("### 🌾 Terreno")
        st.markdown("""
        | Parametro | Tipo | Uso nel Codice |
        |-----------|------|----------------|
        | `hectares` | Numerico [ha] | Calcolo GCR e superficie libera |
        """)
        
        st.markdown("---")
        
        # ==================== FASE 1: GEOMETRIA ====================
        st.markdown("## 📐 Fase 1: Calcoli Geometrici")
        
        st.markdown("""
        ### 🎯 Obiettivo
        Determinare quanto spazio occupano i pannelli e quanto rimane libero per coltivazioni.
        """)
        
        # --- 1.1 Area Pannelli ---
        st.markdown("### 1.1 Superficie Totale Pannelli")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        L'area nominale è la superficie fisica del pannello (senza considerare tilt).
        È il dato usato per calcolare la potenza di picco (Wp).
        """)
        
        st.markdown("**Formula:**")
        st.latex(r"""
        \begin{align}
        A_{\text{pannello}} &= \text{base} \times \text{altezza} \quad [\text{m}^2] \\
        A_{\text{totale}} &= A_{\text{pannello}} \times N_{\text{pannelli}}
        \end{align}
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_panel_metrics()
area_singolo = params["area_pannello"]
superficie_totale = area_singolo * params["num_panels_total"]
        """, language="python")
        
        # --- 1.2 Proiezione Tilt ---
        st.markdown("### 1.2 Proiezione a Terra (con Tilt)")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        Un pannello inclinato di β° occupa meno spazio orizzontale rispetto alla sua altezza fisica.
        
        Esempio: pannello alto 2.5m inclinato 30° → proiezione = 2.5 × cos(30°) = 2.17m
        """)
        
        st.markdown("**Formula:**")
        st.latex(r"""
        \begin{align}
        h_{\text{proiezione}} &= h_{\text{pannello}} \times \cos(\beta) \\
        A_{\text{proiezione}} &= \text{base} \times h_{\text{proiezione}} \\
        A_{\text{proiezione totale}} &= A_{\text{proiezione}} \times N_{\text{pannelli}}
        \end{align}
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_ground_projection()
def calculate_ground_projection(altezza: float, tilt: float) -> float:
    return altezza * math.cos(math.radians(tilt))

# In calculate_panel_metrics()
proiezione_altezza = calculate_ground_projection(
    params["altezza_pannello"], 
    params["tilt_pannello"]
)
proiezione_singolo = params["base_pannello"] * proiezione_altezza
proiezione_totale = proiezione_singolo * params["num_panels_total"]
        """, language="python")
        
        # --- 1.3 Layout Reale ---
        st.markdown("### 1.3 Spazio Occupato (Layout Reale)")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        I pannelli non sono attaccati: serve spazio per:
        - **Manutenzione** (accesso trattori, operatori)
        - **Ridurre ombreggiamenti** tra file
        - **Coltivazioni** tra le file
        """)
        
        st.markdown("**Parametri Layout:**")
        st.markdown("""
        - **Larghezza totale** = pannelli affiancati + spaziature laterali
        - **Profondità totale** = file di pannelli + distanze interfile
        """)
        
        st.markdown("**Formule:**")
        st.latex(r"""
        \text{Se } N_{\text{per fila}} = 1: \quad L_{\text{totale}} = \text{base}
        """)
        st.latex(r"""
        \text{Se } N_{\text{per fila}} > 1: \quad L_{\text{totale}} = (N_{\text{per fila}} - 1) \times P_{\text{laterale}} + \text{base}
        """)
        st.latex(r"""
        \text{Se } N_{\text{file}} = 1: \quad H_{\text{totale}} = h_{\text{proiezione}}
        """)
        st.latex(r"""
        \text{Se } N_{\text{file}} > 1: \quad H_{\text{totale}} = (N_{\text{file}} - 1) \times (h_{\text{proiezione}} + d_{\text{interfile}}) + h_{\text{proiezione}}
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_occupied_space()

# Larghezza
if num_per_row == 1:
    larghezza_totale = base
else:
    larghezza_totale = (num_per_row - 1) * params["pitch_laterale"] + base

# Profondità
if num_rows == 1:
    profondita_totale = proiezione_altezza
else:
    profondita_totale = (num_rows - 1) * (
        proiezione_altezza + params["distanza_interfile"]
    ) + proiezione_altezza

spazio_occupato = larghezza_totale * profondita_totale
        """, language="python")
        
        # --- 1.4 GCR ---
        st.markdown("### 1.4 Ground Coverage Ratio (GCR)")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        Il GCR indica la **percentuale di terreno coperta dalla proiezione dei pannelli**.
        
        È diverso dal "layout occupato" perché considera solo l'ombra dei pannelli, 
        non gli spazi liberi tra loro.
        """)
        
        st.markdown("**Formula:**")
        st.latex(r"""
        \begin{align}
        \text{GCR} &= \frac{A_{\text{proiezione totale}}}{A_{\text{campo}}} \\
        A_{\text{campo}} &= \text{hectares} \times 10000 \, \text{m}^2 \\
        A_{\text{libera}} &= A_{\text{campo}} - A_{\text{proiezione totale}}
        \end{align}
        """)
        
        st.markdown("**Interpretazione Agrivoltaico:**")
        st.markdown("""
        | GCR | Valutazione | Spazio Libero |
        |-----|-------------|---------------|
        | < 30% | ✅ Ottimale | > 70% disponibile per colture |
        | 30-40% | ⚠️ Accettabile | 60-70% disponibile |
        | > 40% | ❌ Critico | < 60% (poco spazio agricolo) |
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_occupied_space()
superficie_campo = params["hectares"] * 10000  # m²
gcr = panel_metrics["proiezione_totale_pannelli"] / superficie_campo
superficie_libera = superficie_campo - panel_metrics["proiezione_totale_pannelli"]
        """, language="python")
        
        st.markdown("---")
        
        # ==================== FASE 2: SOLARE ====================
        st.markdown("## ☀️ Fase 2: Calcoli Solari")
        
        st.markdown("""
        ### 🎯 Obiettivo
        Stimare l'irraggiamento solare che colpisce i pannelli inclinati.
        """)
        
        # --- 2.1 Componenti Radiazione ---
        st.markdown("### 2.1 Componenti Radiazione Solare")
        
        st.markdown("**Teoria Fisica:**")
        
        st.markdown("**1. GHI (Global Horizontal Irradiance)** [W/m²]")
        st.markdown("""
        Radiazione **totale** su superficie **orizzontale**.
        
        Include componente diretta + diffusa.
        """)
        st.latex(r"\text{GHI} = \text{DNI} \times \cos(\theta_{\text{zenith}}) + \text{DHI}")
        
        st.markdown("**2. DNI (Direct Normal Irradiance)** [W/m²]")
        st.markdown("""
        Radiazione **diretta** dal sole, misurata **perpendicolare** ai raggi.
        
        Massima quando sole allo zenith (mezzogiorno estivo).
        """)
        
        st.markdown("**3. DHI (Diffuse Horizontal Irradiance)** [W/m²]")
        st.markdown("""
        Radiazione **diffusa** da cielo/atmosfera (scatter molecolare).
        
        Importante in giornate nuvolose o con alta umidità.
        """)
        
        st.markdown("**4. POA (Plane of Array)** [W/m²]")
        st.markdown("""
        Radiazione **totale** sul piano **inclinato** del pannello.
        
        Include:
        - Componente diretta (dipende da angolo incidenza)
        - Componente diffusa (dal cielo)
        - Componente riflessa (albedo del suolo)
        """)
        st.latex(r"""
        \text{POA} = \text{DNI} \times \cos(\theta_i) + \text{DHI}_{\text{pannello}} + \text{GHI} \times \text{albedo} \times F_{\text{ground}}
        """)
        
        # --- 2.2 Modello Clearsky ---
        st.markdown("### 2.2 Modello Clearsky (Ineichen)")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        Il modello **Ineichen** stima l'irraggiamento in condizioni di **cielo sereno** 
        (assenza di nuvole).
        
        **Perché Clearsky?**
        - ✅ Fornisce **limite superiore** della produzione
        - ✅ Non richiede dati meteorologici storici
        - ✅ Utile per dimensionamento ottimistico
        - ❌ **Sovrastima** la produzione reale del 20-30%
        
        **Come Funziona:**
        1. Calcola posizione sole (elevazione, azimuth)
        2. Stima attenuazione atmosferica (Linke turbidity)
        3. Calcola DNI, DHI, GHI teorici
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_all_pv()
import pvlib
import pandas as pd

# 1. Serie temporale oraria
times = pd.date_range(
    start=params["data"],
    end=params["data"] + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
    freq="1h",
    tz=params["timezone"]
)

# 2. Posizione sole
solpos = pvlib.solarposition.get_solarposition(
    times, 
    params["lat"], 
    params["lon"]
)
# Output: solpos['zenith'], solpos['azimuth'], solpos['elevation']

# 3. Clearsky Ineichen
site = pvlib.location.Location(params["lat"], params["lon"], tz=params["timezone"])
clearsky = site.get_clearsky(times, model="ineichen")
# Output: clearsky['ghi'], clearsky['dni'], clearsky['dhi']
        """, language="python")
        
        # --- 2.3 Calcolo POA ---
        st.markdown("### 2.3 Calcolo POA (Irraggiamento sul Pannello)")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        Il pannello inclinato riceve radiazione diversa da una superficie orizzontale.
        
        **Fattori Chiave:**
        1. **Angolo di incidenza** (θ_i) → determina componente diretta
        2. **View factor cielo** → frazione cielo visibile (diffusa)
        3. **View factor suolo** → frazione suolo visibile (riflessa)
        """)
        
        st.markdown("**Formula Completa:**")
        st.latex(r"""
        \begin{align}
        \text{POA} &= \text{POA}_{\text{diretta}} + \text{POA}_{\text{diffusa}} + \text{POA}_{\text{riflessa}} \\
        \text{POA}_{\text{diretta}} &= \text{DNI} \times \cos(\theta_i) \\
        \text{POA}_{\text{diffusa}} &= \text{DHI} \times \frac{1 + \cos(\beta)}{2} \\
        \text{POA}_{\text{riflessa}} &= \text{GHI} \times \text{albedo} \times \frac{1 - \cos(\beta)}{2}
        \end{align}
        """)
        
        st.markdown("Dove:")
        st.markdown("""
        - **θ_i** = angolo tra raggi solari e normale al pannello
        - **β** = tilt pannello
        - **(1+cos(β))/2** = view factor cielo (modello isotropico)
        - **(1-cos(β))/2** = view factor suolo
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_poa_global()
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

poa_global = poa['poa_global']  # W/m²
        """, language="python")
        
        st.markdown("---")
        
        # ==================== FASE 3: PRODUZIONE ====================
        st.markdown("## ⚡ Fase 3: Produzione Elettrica")
        
        st.markdown("""
        ### 🎯 Obiettivo
        Convertire radiazione solare in energia elettrica, considerando perdite termiche.
        """)
        
        # --- 3.1 Temperatura Celle ---
        st.markdown("### 3.1 Temperatura Celle Fotovoltaiche")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        Le celle fotovoltaiche si scaldano sotto il sole, causando:
        - ❌ Riduzione efficienza (tipicamente -0.4% per °C)
        - ❌ Riduzione tensione output
        - ✅ Lieve aumento corrente (trascurabile)
        
        **Effetto Pratico:**
        - Pannello 25°C → 100% efficienza
        - Pannello 50°C → ~90% efficienza
        - Pannello 70°C → ~82% efficienza
        """)
        
        st.markdown("**Formula NOCT:**")
        st.latex(r"""
        T_{\text{cell}} = T_{\text{ambiente}} + \frac{\text{POA}}{800} \times (\text{NOCT} - 20)
        """)
        
        st.markdown("Dove:")
        st.markdown("""
        - **NOCT** = Nominal Operating Cell Temperature [°C]
          - Temperatura celle con: POA=800 W/m², T_amb=20°C, vento=1 m/s
          - Tipicamente: 42-47°C
        - **800 W/m²** = irraggiamento di riferimento NOCT
        - **20°C** = temperatura ambiente di riferimento NOCT
        """)
        
        st.markdown("**Stima Temperatura Ambiente:**")
        st.markdown("""
        Il simulatore usa un **modello sinusoidale** stagionale:
        
        1. Stima temperatura media stagionale (corretta per latitudine)
        2. Applica oscillazione giornaliera (minimo h6, massimo h14)
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In estimate_ambient_temperature()
def estimate_ambient_temperature(times, lat):
    month = times[0].month
    
    # Temperature medie stagionali (corrette per latitudine)
    if month in [12, 1, 2]:  # Inverno
        T_media = 8 - (lat - 40) * 0.5
        escursione = 6
    elif month in [3, 4, 5]:  # Primavera
        T_media = 15 - (lat - 40) * 0.3
        escursione = 8
    elif month in [6, 7, 8]:  # Estate
        T_media = 26 - (lat - 40) * 0.4
        escursione = 10
    else:  # Autunno
        T_media = 16 - (lat - 40) * 0.3
        escursione = 7
    
    # Sinusoide oraria (min h6, max h14)
    hours = times.hour
    T_amb = T_media + escursione * pd.Series(
        [math.sin(math.pi * (h - 6) / 12) for h in hours],
        index=times
    )
    return T_amb

# In calculate_pv_production()
T_amb = estimate_ambient_temperature(times, params["lat"])
T_cell = T_amb + (poa_global / 800) * (params["noct"] - 20)
        """, language="python")
        
        # --- 3.2 Efficienza Corretta ---
        st.markdown("### 3.2 Efficienza Corretta per Temperatura")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        L'efficienza del pannello diminuisce linearmente con la temperatura.
        
        **Coefficiente Temperatura (γ):**
        - Tipicamente: **-0.4% per °C** (silicio cristallino)
        - Pannelli premium: -0.3%/°C (celle HJT, PERC+)
        - Thin-film: -0.2%/°C (CdTe, CIGS)
        """)
        
        st.markdown("**Formula:**")
        st.latex(r"""
        \eta_{\text{corretta}} = \eta_{\text{STC}} \times \left[1 + \gamma \times (T_{\text{cell}} - 25°\text{C})\right]
        """)
        
        st.markdown("Dove:")
        st.markdown("""
        - **η_STC** = efficienza a Standard Test Conditions (25°C, 1000 W/m²)
        - **γ** = coefficiente temperatura [%/°C] (negativo!)
        """)
        
        st.markdown("**Esempio Numerico:**")
        st.markdown("""
        ```
        η_STC = 20%
        γ = -0.4%/°C
        T_cell = 50°C
        
        η_corretta = 0.20 × [1 + (-0.004) × (50 - 25)]
                   = 0.20 × [1 - 0.1]
                   = 0.20 × 0.9
                   = 0.18 = 18%
        
        → Perdita 10% per +25°C
        ```
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_pv_production()
eff_corr = params["eff"] * (1 + params["temp_coeff"] * (T_cell - 25))
        """, language="python")
        
        # --- 3.3 Potenza Istantanea ---
        st.markdown("### 3.3 Potenza Elettrica Istantanea")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        La potenza elettrica generata dipende da:
        1. Radiazione incidente (POA)
        2. Area del pannello
        3. Efficienza (corretta per temperatura)
        4. Perdite di sistema
        """)
        
        st.markdown("**Formula:**")
        st.latex(r"""
        P_{\text{istantanea}} = \text{POA} \times A_{\text{pannello}} \times \eta_{\text{corretta}} \times (1 - L_{\text{sistema}})
        """)
        
        st.markdown("**Perdite di Sistema (L):**")
        st.markdown("""
        | Componente | Perdita Tipica |
        |------------|----------------|
        | Cavi DC | 1-2% |
        | Inverter | 2-3% |
        | Trasformatore | 1-2% |
        | Sporcizia pannelli | 2-5% |
        | Mismatch moduli | 1-2% |
        | Ombreggiamenti | 0-10% |
        | **TOTALE** | **8-15%** |
        
        > Il simulatore usa un valore unico configurabile (default 10%).
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_pv_production()

# Potenza singolo pannello [W]
power_single = (
    poa_global * 
    params["area_pannello"] * 
    eff_corr * 
    (1 - params["losses"])
).round(0).astype(int)

# Potenza totale impianto [W]
power_total = power_single * params["num_panels_total"]
        """, language="python")
        
        # --- 3.4 Energia Giornaliera ---
        st.markdown("### 3.4 Energia Giornaliera")
        
        st.markdown("**Teoria Fisica:**")
        st.markdown("""
        L'energia giornaliera si ottiene **sommando** le potenze orarie.
        
        Equivalente a integrare la curva di potenza nel tempo:
        """)
        st.latex(r"""
        E_{\text{giornaliera}} = \sum_{h=0}^{23} P_h \times \Delta t = \sum_{h=0}^{23} P_h \times 1\text{h}
        """)
        
        st.markdown("**Unità di Misura:**")
        st.markdown("""
        - Potenza oraria: **Watt [W]**
        - Energia giornaliera: **Watt-ora [Wh]**
        - Conversione: 1 kWh = 1000 Wh
        """)
        
        st.markdown("**Implementazione Python:**")
        st.code("""
# In calculate_pv_production()

# Energia giornaliera [Wh]
energy_single = power_single.sum()  # Somma 24 valori orari
energy_total = power_total.sum()

# Energia per m² [Wh/m²]
energy_single_m2 = energy_single / params["area_pannello"]
energy_total_m2 = energy_total / (params["area_pannello"] * params["num_panels_total"])
        """, language="python")
        
        st.markdown("---")
        
        # ==================== LIMITAZIONI ====================
        st.markdown("## ⚠️ Limitazioni Attuali")
        
        st.markdown("""
        ### ❌ Cosa NON Calcola (Ancora)
        
        Questa sezione è **fondamentale** per comprendere i limiti del simulatore.
        """)
        
        # --- Limitazione 1 ---
        st.markdown("### 1️⃣ Altezza Pannelli dal Suolo")
        st.markdown("""
        **Parametro Mancante:** `altezza_suolo` [m]
        
        **Cosa Non Viene Calcolato:**
        - ❌ Effetto ventilazione celle (raffreddamento naturale)
        - ❌ Ombreggiamento colture sotto pannelli
        - ❌ Altezza effettiva per PAR (radiazione fotosintetica al suolo)
        - ❌ Verifica accessibilità mezzi agricoli
        
        **Impatto:**
        - Temperatura celle potrebbe essere **sovrastimata** (meno ventilazione)
        - Nessuna stima radiazione disponibile per colture
        
        **Come Implementarlo:**
        ```python
        # In sidebar.py - aggiungere:
        altezza_suolo = st.number_input(
            "Altezza dal Suolo [m]",
            value=2.0,
            min_value=0.5,
            max_value=6.0,
            step=0.1
        )
        
        # In calculations.py - usare per:
        # 1. Correzione ventilazione celle
        # 2. Calcolo ombra su colture
        # 3. Verifica accessibilità (h_min = 2.2m per trattori)
        ```
        """)
        
        # --- Limitazione 2 ---
        st.markdown("### 2️⃣ Ombreggiamento Mutuo tra Pannelli")
        st.markdown("""
        **Cosa Non Viene Calcolato:**
        - ❌ Verifica geometrica distanza minima anti-ombra
        - ❌ Perdite produzione da ombreggiamento file anteriori
        - ❌ Analisi ore di sole effettive per ogni fila
        
        **Cosa Viene Fatto Ora:**
        - ✅ GCR e spazi liberi (ma senza verifica ombre)
        - ✅ Distanza interfile (ma senza calcolo ombre)
        
        **Impatto:**
        - Layout potrebbe causare ombre non rilevate
        - Produzione potrebbe essere **sovrastimata** (file posteriori ombreggiate)
        
        **Come Implementarlo:**
        ```python
        # Formula distanza minima anti-ombra:
        d_min = h_pannello × sin(tilt) / tan(elevazione_solare_min)
        
        # Dove elevazione_solare_min = angolo sole a solstizio inverno h12
        ```
        """)
        
        # --- Limitazione 3 ---
        st.markdown("### 3️⃣ Dati Meteorologici Reali")
        st.markdown("""
        **Modello Attuale:** Clearsky (cielo sereno ideale)
        
        **Cosa Manca:**
        - ❌ Copertura nuvolosa reale
        - ❌ Precipitazioni
        - ❌ Neve/ghiaccio su pannelli
        - ❌ Vento reale (raffreddamento celle)
        - ❌ Umidità (sporcizia pannelli)
        
        **Impatto:**
        - Produzione **sovrastimata del 20-30%** rispetto a condizioni reali
        - Nessuna considerazione eventi estremi
        
        **Come Migliorare:**
        ```python
        # Integrare dati TMY (Typical Meteorological Year):
        # - PVGIS (EU)
        # - NSRDB (USA)
        # - Meteonorm
        
        # Esempio con pvlib:
        weather = pvlib.iotools.get_pvgis_tmy(lat, lon)
        # Include: GHI, DNI, DHI, T_amb, vento, pressione
        ```
        """)
        
        # --- Limitazione 4 ---
        st.markdown("### 4️⃣ Proiezione Temporale")
        st.markdown("""
        **Limitazione Attuale:** Solo 1 giorno
        
        **Cosa Manca:**
        - ❌ Simulazione mensile/annuale
        - ❌ Variazione stagionale produzione
        - ❌ Trend degradazione pannelli (0.5-0.8%/anno)
        - ❌ Impatto manutenzione programmata
        
        **Impatto:**
        - Nessuna stima produzione annuale
        - Impossibile calcolare ROI o payback
        
        **Come Implementarlo:**
        ```python
        # Loop su 365 giorni:
        for day in pd.date_range(start='2025-01-01', end='2025-12-31', freq='D'):
            results_day = calculate_all_pv(params)
            annual_production += results_day['energy_total_Wh']
        
        # Applicare degradazione:
        for year in range(1, 26):  # 25 anni vita utile
            degradation_factor = (1 - 0.005) ** year
            production_year = annual_production * degradation_factor
        ```
        """)
        
        # --- Limitazione 5 ---
        st.markdown("### 5️⃣ Impatto su Colture")
        st.markdown("""
        **Cosa Manca Completamente:**
        - ❌ PAR (Photosynthetically Active Radiation) disponibile al suolo
        - ❌ Distribuzione spaziale ombra su colture
        - ❌ Effetto microclima (T, umidità sotto pannelli)
        - ❌ Compatibilità colture con ombreggiamento
        - ❌ Stima resa agricola
        
        **Impatto:**
        - Nessuna valutazione agronomica
        - Impossibile stimare dual-use efficiency
        
        **Metriche Agrivoltaico Mancanti:**
        ```python
        # Land Equivalent Ratio (LER):
        LER = (Prod_energia / Prod_energia_solo_FV) + 
              (Prod_agricola / Prod_agricola_solo_campo)
        # Obiettivo: LER > 1 (sinergia positiva)
        
        # PAR al suolo:
        PAR_suolo = PAR_incidente × (1 - τ_pannelli) × f_ombra
        # τ_pannelli = trasmittanza pannelli (~0%)
        # f_ombra = frazione area ombreggiata
        ```
        """)
        
        # --- Limitazione 6 ---
        st.markdown("### 6️⃣ Analisi Economica")
        st.markdown("""
        **Cosa Manca:**
        - ❌ CAPEX (costi installazione): €/kWp
        - ❌ OPEX (manutenzione): €/anno
        - ❌ Ricavi energetici: €/kWh
        - ❌ Ricavi agricoli: €/ha
        - ❌ Incentivi (Conto Energia, FiT)
        - ❌ ROI, payback time, NPV
        
        **Impatto:**
        - Nessuna valutazione finanziaria
        - Impossibile confrontare scenari
        
        **Parametri Economici Tipici:**
        | Voce | Valore Tipico (Italia 2025) |
        |------|------------------------------|
        | CAPEX | 800-1200 €/kWp |
        | OPEX | 15-25 €/kWp/anno |
        | Tariffa vendita | 0.08-0.12 €/kWh |
        | Tariffa autoconsumo | 0.20-0.30 €/kWh |
        | Vita utile | 25-30 anni |
        | Tasso sconto | 3-5% |
        """)
        
        st.markdown("---")
        
        # ==================== RIEPILOGO FLUSSO ====================
        st.markdown("## 🔄 Riepilogo Flusso di Calcolo")
        
        st.markdown("""
        ```
        ┌─────────────────────────────────────────────┐
        │          INPUT UTENTE (sidebar.py)          │
        │  • Localizzazione (comune, lat, lon, data)  │
        │  • Layout (pannelli/fila, n. file)          │
        │  • Dimensioni (base, altezza)               │
        │  • Spaziatura (interfile, pitch)            │
        │  • Orientamento (tilt, azimuth)             │
        │  • Elettrico (eff, NOCT, losses)            │
        │  • Campo (hectares)                         │
        └──────────────────┬──────────────────────────┘
                           ↓
        ┌─────────────────────────────────────────────┐
        │    FASE 1: GEOMETRIA (calculations.py)      │
        │  calculate_panel_metrics()                  │
        │    → Area nominale pannelli                 │
        │    → Proiezione a terra (con tilt)          │
        │  calculate_occupied_space()                 │
        │    → Larghezza/profondità layout            │
        │    → GCR (Ground Coverage Ratio)            │
        │    → Superficie libera                      │
        └──────────────────┬──────────────────────────┘
                           ↓
        ┌─────────────────────────────────────────────┐
        │   FASE 2: IRRAGGIAMENTO (calculations.py)   │
        │  pvlib.solarposition.get_solarposition()    │
        │    → Elevazione, azimuth sole               │
        │  pvlib.location.get_clearsky()              │
        │    → GHI, DNI, DHI (modello Ineichen)       │
        │  pvlib.irradiance.get_total_irradiance()    │
        │    → POA (piano pannelli inclinato)         │
        │  estimate_ambient_temperature()             │
        │    → T ambiente (modello sinusoidale)       │
        └──────────────────┬──────────────────────────┘
                           ↓
        ┌─────────────────────────────────────────────┐
        │  FASE 3: PRODUZIONE (calculations.py)       │
        │  calculate_pv_production()                  │
        │    → T celle = f(T_amb, POA, NOCT)          │
        │    → η corretta = f(T_celle, γ)             │
        │    → P istantanea = POA × A × η × (1-L)     │
        │    → E giornaliera = Σ(P oraria)            │
        └──────────────────┬──────────────────────────┘
                           ↓
        ┌─────────────────────────────────────────────┐
        │         OUTPUT FINALE (metrics.py)          │
        │  • Irraggiamento: GHI, DNI, DHI, POA        │
        │  • Geometria: GCR, spazio libero            │
        │  • Produzione: kWh/giorno, T celle          │
        │  • Grafici: serie temporali orarie          │
        └─────────────────────────────────────────────┘
        ```
        """)
        
        st.markdown("---")
        
        # ==================== FILE SORGENTI ====================
        st.markdown("## 📁 Struttura Codice Sorgente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### File Principali
            
            **`app.py`**
            - Entry point applicazione
            - Setup Streamlit
            - Orchestrazione flusso
            
            **`sidebar.py`**
            - Raccolta input utente
            - Widget UI (number_input, slider)
            - Geocoding comune → GPS
            
            **`calculations.py`**
            - ⭐ **Core calcoli scientifici**
            - Geometria, solare, produzione
            - Uso pvlib per irraggiamento
            
            **`metrics.py`**
            - Visualizzazione risultati
            - Card metriche responsive
            - Layout desktop/mobile
            """)
        
        with col2:
            st.markdown("""
            ### File Supporto
            
            **`config.py`**
            - Costanti fisiche
            - Parametri default
            - CSS globale
            
            **`maps.py`**
            - Mappa interattiva (Folium)
            - Info box parametri input
            
            **`guida.py`**
            - ⭐ **Questo file**
            - Documentazione completa
            
            **`deploy.py`**
            - Script automazione deploy
            - Git commit/push
            - Streamlit Cloud sync
            """)
        
        st.markdown("---")
        
        # ==================== FUNZIONI CHIAVE ====================
        st.markdown("## 🔑 Funzioni Chiave da Conoscere")
        
        st.markdown("### `calculate_all_pv()` - Funzione Principale")
        st.code("""
def calculate_all_pv(params: dict) -> dict:
    \"\"\"
    Calcola TUTTI i parametri PV
    
    Args:
        params: dizionario completo parametri input
    
    Returns:
        dict con:
            - times: serie temporale oraria
            - GHI_Wm2, DNI_Wm2, DHI_Wm2, POA_Wm2: irraggiamento
            - GHI_Whm2, ...: totali giornalieri
            - superficie_totale_pannelli, gcr, superficie_libera
            - power_single_W, power_total_W: potenza oraria
            - energy_single_Wh, energy_total_Wh: energia giornaliera
            - T_cell_avg: temperatura media celle
    \"\"\"
    # 1. Serie temporale
    times = pd.date_range(...)
    
    # 2. Geometria
    panel_metrics = calculate_panel_metrics(params)
    occupied_space = calculate_occupied_space(params, panel_metrics)
    
    # 3. Solare
    solpos = calculate_solar_position(times, lat, lon)
    clearsky = calculate_clearsky_irradiance(times, lat, lon, tz)
    poa_global = calculate_poa_global(clearsky, solpos, tilt, azimuth, albedo)
    T_amb = estimate_ambient_temperature(times, lat)
    
    # 4. Produzione
    production = calculate_pv_production(params, poa_global, T_amb)
    
    return {...}  # Merge tutti i risultati
        """, language="python")
        
        st.markdown("### Funzioni Geometriche")
        st.code("""
calculate_ground_projection(altezza, tilt)
    → proiezione = altezza × cos(tilt)

calculate_panel_metrics(params)
    → superficie_totale, proiezione_singolo, proiezione_totale

calculate_occupied_space(params, panel_metrics)
    → spazio_occupato, gcr, superficie_libera
        """, language="python")
        
        st.markdown("### Funzioni Solari")
        st.code("""
calculate_solar_position(times, lat, lon)
    → pvlib.solarposition.get_solarposition()
    → elevazione, azimuth, zenith sole

calculate_clearsky_irradiance(times, lat, lon, tz)
    → pvlib.location.get_clearsky(model='ineichen')
    → GHI, DNI, DHI

calculate_poa_global(clearsky, solpos, tilt, azimuth, albedo)
    → pvlib.irradiance.get_total_irradiance()
    → POA sul piano inclinato

estimate_ambient_temperature(times, lat)
    → Modello sinusoidale stagionale
    → T_media + escursione × sin(π(h-6)/12)
        """, language="python")
        
        st.markdown("### Funzioni Produzione")
        st.code("""
calculate_pv_production(params, poa_global, T_amb)
    1. T_cell = T_amb + (POA/800) × (NOCT-20)
    2. eff_corr = eff × [1 + temp_coeff × (T_cell-25)]
    3. P_inst = POA × A × eff_corr × (1-losses)
    4. E_day = Σ(P_inst)
    
    → power_single_W, power_total_W
    → energy_single_Wh, energy_total_Wh
    → energy_Wh_m2, T_cell_avg
        """, language="python")
        
        st.markdown("---")

        # ==================== BIBLIOGRAFIA ====================
        st.markdown("## Bibliografia e Riferimenti")
        st.markdown("""
        1. Duffie, J.A., Beckman, W.A., *Solar Engineering of Thermal Processes*, 4th Ed., Wiley, 2013.
        2. PVLib Python Documentation – [https://pvlib-python.readthedocs.io](https://pvlib-python.readthedocs.io)
        3. Ineichen, P., *A broadband simplified version of the Solis clear sky model*, Solar Energy, 2008.
        4. Perez, R., Seals, R., Ineichen, P., *Modeling Daylight Availability and Irradiance Components*, Solar Energy, 1990.
        5. IEA PVPS, *Trends in Photovoltaic Applications*, International Energy Agency.
        """)
