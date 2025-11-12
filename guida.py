"""
Documentazione tecnica dei calcoli del simulatore fotovoltaico
"""

import streamlit as st


def show_pv_guide():
    """Visualizza documentazione tecnica completa con tabs"""
    
    with st.expander("📘 GUIDA TECNICA", expanded=False):
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📋 Input",
            "⚙️ Calcoli Geometrici",
            "☀️ Calcoli Solari",
            "⚡ Produzione Elettrica",
            "🌽 Calcoli Agronomici",
            "📊 Metriche Output",
            "📚 Bibliografia"
        ])
        
        with tab1:
            st.markdown("""
            ## 1. PARAMETRI DI INPUT
            
            ### 1.1 Localizzazione e Temporizzazione
            
            #### Geocoding
            - **Comune**: stringa di testo inserita dall'utente (default: "Roma")
            - **Geocoding automatico**: 
              - Libreria: `geopy.geocoders.Nominatim`
              - User agent: "resfarm@monitoring.com"
              - Query: `"{comune}, Italia"`
              - Timeout: 10 secondi
              - Cache: `@lru_cache(maxsize=200)` per evitare chiamate ripetute
              - Retry: 3 tentativi con backoff esponenziale in caso di timeout
            - **Latitudine, Longitudine** [°]: estratte da `location.latitude`, `location.longitude`
            - **Fallback manuale**: se geocoding fallisce, richiesta input numerico utente (default: 41.9°, 12.5°)
            
            **Implementazione**:
            ```python
            from geopy.geocoders import Nominatim
            from functools import lru_cache
            
            @lru_cache(maxsize=200)
            def cached_geocode(comune: str):
                geolocator = Nominatim(user_agent="resfarm@monitoring.com", timeout=10)
                return geolocator.geocode(f"{comune}, Italia")
            ```
            
            #### Temporizzazione
            - **Data simulazione**: `date.today()` o selezione utente tramite `st.date_input()`
            - **Timezone**: fisso `ZoneInfo("Europe/Rome")` dalla libreria `zoneinfo`
            - **Serie temporale**: `pd.date_range()` oraria per 24h, timezone-aware
            
            **Implementazione**:
            ```python
            from zoneinfo import ZoneInfo
            
            TIMEZONE_OBJ = ZoneInfo("Europe/Rome")
            
            times = pd.date_range(
                start=pd.Timestamp(data),
                end=pd.Timestamp(data) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
                freq="1h",
                tz=TIMEZONE_OBJ
            )
            ```
            
            ---
            
            ### 1.2 Configurazione Layout Pannelli
            
            #### Disposizione
            - **Pannelli per fila** ($N_{fila}$): numero di pannelli allineati orizzontalmente (default: 5)
            - **Numero file** ($N_{file}$): numero di righe di pannelli (default: 2)
            - **Totale pannelli** ($N_{tot}$): calcolato automaticamente
            
            $$N_{tot} = N_{fila} \times N_{file}$$
            
            **Implementazione**:
            ```python
            num_panels_total = num_panels_per_row * num_rows
            ```
            
            #### Dimensioni Modulo
            - **Lato maggiore** [m] ($L_{mag}$): dimensione lungo il lato più lungo (default: 2.5 m)
            - **Lato minore** [m] ($L_{min}$): dimensione lungo il lato più corto (default: 2.0 m)
            - **Area pannello** [m²] ($A_{pan}$): superficie nominale del modulo
            
            $$A_{pan} = L_{mag} \times L_{min}$$
            
            **Implementazione**:
            ```python
            area_pannello = lato_maggiore * lato_minore
            ```
            
            #### Spaziature
            - **Carreggiata** [m]: distanza tra le file di pannelli, misurata tra bordi posteriori consecutivi (default: 5.0 m)
            - **Pitch laterale** [m]: distanza tra i centri di pannelli adiacenti nella stessa fila (default: 3.0 m)
            - **Altezza dal suolo** [m]: distanza verticale tra terreno e bordo inferiore del pannello (default: 1.0 m)
            
            **Nota**: la carreggiata determina lo spazio disponibile per il passaggio di mezzi agricoli e la coltivazione.
            
            ---
            
            ### 1.3 Orientamento Pannelli
            
            #### Angoli
            - **Tilt (β)** [°]: angolo di inclinazione rispetto al piano orizzontale
              - Range: 0° (orizzontale) - 90° (verticale)
              - Default: 30°
              - Input: slider `st.slider()`
            
            - **Azimuth (α)** [°]: orientamento rispetto al Nord geografico
              - Range: 0° - 360°
              - Convenzione: 0° = Nord, 90° = Est, 180° = Sud, 270° = Ovest
              - Default: 180° (orientamento a Sud)
              - Input: slider `st.slider()`
            
            **Nota**: in Italia, l'orientamento ottimale è generalmente Sud (180°) con tilt pari alla latitudine ±10°.
            
            ---
            
            ### 1.4 Caratteristiche Elettriche Modulo Fotovoltaico
            
            #### Efficienza e Temperatura
            - **Efficienza nominale (η)** [%]: rapporto tra potenza elettrica prodotta e irraggiamento incidente in condizioni STC (Standard Test Conditions: 25°C, 1000 W/m², AM 1.5)
              - Range: 0.1% - 100%
              - Default: 20% (0.20)
              - Input: `st.number_input()` con conversione percentuale → frazione
            
            - **NOCT** [°C]: Nominal Operating Cell Temperature - temperatura di funzionamento delle celle con irraggiamento 800 W/m², temperatura ambiente 20°C, velocità vento 1 m/s, open circuit
              - Range: 20°C - 60°C
              - Default: 45°C
              - Standard: IEC 61215
            
            - **Coefficiente di temperatura (γ)** [%/°C]: variazione percentuale di potenza per grado di temperatura delle celle rispetto a 25°C
              - Tipicamente negativo: aumenta T → diminuisce potenza
              - Range: -0.2% a -0.5% per °C
              - Default: -0.4%/°C (-0.004)
              - Input: `st.number_input()` con conversione percentuale → frazione
            
            **Implementazione conversione**:
            ```python
            eff = st.number_input("Efficienza [%]", value=20.0, ...) / 100
            temp_coeff = st.number_input("Coeff. γ [%/°C]", value=-0.4, ...) / 100
            ```
            
            #### Perdite di Sistema
            - **Perdite sistema (L)** [%]: perdite complessive non legate alla temperatura
              - Include: perdite ohmiche nei cavi, inverter, mismatch, sporcizia, ombreggiamenti parziali, degrado
              - Range: 0% - 50%
              - Default: 10% (0.10)
            
            - **Albedo (ρ)**: coefficiente di riflessione del suolo
              - Frazione di radiazione solare riflessa dalla superficie
              - Range: 0.0 (superficie nera, assorbimento totale) - 1.0 (superficie speculare)
              - Valori tipici:
                - Terreno agricolo: 0.20 - 0.25
                - Erba: 0.15 - 0.25
                - Sabbia: 0.30 - 0.40
                - Neve: 0.80 - 0.90
              - Default: 0.20
              - Input: `st.number_input()` con step 0.05
            
            ---
            
            ### 1.5 Parametri Campo e Coltura
            
            #### Superficie
            - **Ettari totali**: estensione del terreno disponibile
              - Default: 1.0 ha
              - Conversione: `superficie_campo_m2 = hectares × 10000`
            
            - **Superficie campo** [m²] ($A_{campo}$): 
            
            $$A_{campo} = \text{ettari} \times 10000$$
            
            **Implementazione**:
            ```python
            from config import HECTARE_M2  # HECTARE_M2 = 10000
            
            superficie_campo = hectares * HECTARE_M2
            ```
            
            #### Coltura
            - **Tipo coltura**: selezione da database interno
            - **Categorie disponibili**:
              - Piante basse: Microgreens, Ortaggi a foglia, Tuberi, Ortaggi da frutto bassi
              - Piante alte: Cereali, Legumi, Ortaggi da frutto alti, Frutta (alberi e arbusti), Viti, Piante ornamentali alte
            - Default: "Microgreens"
            - Input: `st.selectbox()` con lista predefinita
            
            **Database DLI interno**: ogni coltura ha associati requisiti di luce ($DLI_{min}$, $DLI_{opt}$) definiti in `agri_calculations.py` nel dizionario `DLI_REQUIREMENTS`.
            """)
        
        with tab2:
            st.markdown("""
            ## 2. CALCOLI GEOMETRICI
            **Modulo**: `calculations.py`  
            **Funzioni**: `calculate_ground_projection()`, `calculate_panel_metrics()`, `calculate_occupied_space()`, `calculate_max_panels()`
            
            ---
            
            ### 2.1 Proiezione Pannello al Suolo
            
            #### Formula Teorica
            Un pannello inclinato di angolo β rispetto all'orizzonte proietta al suolo un'area ridotta rispetto alla sua area nominale. La proiezione è calcolata come:
            
            $$A_{proj} = A_{pan} \cdot \cos(\beta)$$
            
            dove:
            - $A_{proj}$ = area proiettata al suolo [m²]
            - $A_{pan}$ = area nominale del pannello [m²]
            - $\beta$ = tilt del pannello [radianti]
            
            #### Implementazione
            ```python
            def calculate_ground_projection(area: float, tilt: float) -> float:
                return area * math.cos(math.radians(tilt))
            
            # Applicazione
            proiezione_singolo = calculate_ground_projection(area_pannello, tilt_pannello)
            proiezione_totale = proiezione_singolo * num_panels_total
            ```
            
            **Esempio numerico**:
            - Pannello 2.5 m × 2.0 m = 5.0 m²
            - Tilt = 30°
            - Proiezione = 5.0 × cos(30°) = 5.0 × 0.866 = 4.33 m²
            
            ---
            
            ### 2.2 Ground Coverage Ratio (GCR)
            
            #### Definizione
            Il GCR rappresenta la frazione di terreno effettivamente coperta dalla proiezione dei pannelli fotovoltaici.
            
            #### Formula Teorica
            
            $$GCR = \frac{\sum A_{proj}}{ A_{campo}} = \frac{A_{proj,singolo} \times N_{tot}}{A_{campo}}$$
            
            dove:
            - $\sum A_{proj}$ = somma delle proiezioni di tutti i pannelli [m²]
            - $A_{campo}$ = superficie totale disponibile [m²]
            - $N_{tot}$ = numero totale pannelli
            
            #### Implementazione
            ```python
            def calculate_occupied_space(params: dict, panel_metrics: dict) -> dict:
                superficie_campo = params["hectares"] * HECTARE_M2
                gcr = panel_metrics["proiezione_totale_pannelli"] / superficie_campo
                return {"gcr": gcr, ...}
            ```
            
            #### Interpretazione
            - **GCR < 0.3**: bassa densità, molto spazio libero per agricoltura
            - **GCR 0.3 - 0.4**: densità moderata, configurazione agrivoltaica tipica
            - **GCR > 0.4**: alta densità, possibile competizione con colture (evidenziato in rosso nell'interfaccia)
            
            **Nota**: il GCR è calcolato sulla base della sola proiezione dei pannelli, non considera le spaziature di layout (carreggiata, pitch).
            
            ---
            
            ### 2.3 Superficie Libera
            
            #### Formula Teorica
            La superficie libera è il terreno non occupato dalla proiezione dei pannelli:
            
            $$A_{libera} = A_{campo} - \sum A_{proj}$$
            
            #### Implementazione
            ```python
            superficie_libera = superficie_campo - panel_metrics["proiezione_totale_pannelli"]
            superficie_libera = max(0, superficie_libera)  # clamp a zero se negativo
            ```
            
            **Nota**: la superficie libera rappresenta lo spazio teoricamente disponibile per la coltivazione, ma deve considerare anche le carreggiate e gli spazi di servizio.
            
            ---
            
            ### 2.4 Dimensionamento Massimo Installabile
            
            #### Metodo di Calcolo
            Data una superficie quadrata approssimata, determina il numero massimo di pannelli installabili considerando:
            - Pitch laterale (distanza tra pannelli nella stessa fila)
            - Carreggiata (distanza tra file)
            - Dimensioni del pannello
            
            #### Formule
            
            Lato stimato del campo (approssimazione quadrata):
            $$L_{campo} = \sqrt{A_{campo}}$$
            
            Pannelli per fila:
            $$N_{fila,max} = \left\lfloor \frac{L_{campo}}{pitch_{laterale}} \right\rfloor$$
            
            Numero file:
            $$N_{file,max} = \left\lfloor \frac{L_{campo}}{L_{min} + carreggiata} \right\rfloor$$
            
            Totale pannelli:
            $$N_{tot,max} = N_{fila,max} \times N_{file,max}$$
            
            #### Implementazione
            ```python
            def calculate_max_panels(params: dict) -> dict:
                campo_m2 = params["hectares"] * HECTARE_M2
                lato_campo = math.sqrt(campo_m2)
                
                # Pannelli per fila
                max_panels_per_row = int(lato_campo / params["pitch_laterale"])
                spazio_laterale_libero = lato_campo - max_panels_per_row * params["pitch_laterale"]
                
                # Numero file
                spazio_per_fila = params["lato_minore"] + params["carreggiata"]
                max_rows = int(lato_campo / spazio_per_fila)
                spazio_longitudinale_libero = lato_campo - max_rows * spazio_per_fila
                
                # Totale
                total_panels = max_panels_per_row * max_rows
                
                return {
                    "lato_campo_stimato_m": lato_campo,
                    "max_panels_per_row": max_panels_per_row,
                    "max_rows": max_rows,
                    "total_panels": total_panels,
                    "spazio_laterale_libero_m": spazio_laterale_libero,
                    "spazio_longitudinale_libero_m": spazio_longitudinale_libero
                }
            ```
            
            **Nota**: questo calcolo fornisce una stima del numero massimo di pannelli installabili secondo vincoli geometrici, assumendo campo quadrato. Per geometrie irregolari, è necessaria analisi caso per caso.
            """)
        
        with tab3:
            st.markdown("""
            ## 3. CALCOLI SOLARI
            **Modulo**: `calculations.py`  
            **Libreria principale**: `pvlib-python` v0.9+
            
            ---
            
            ### 3.1 Posizione Solare
            
            #### Funzione pvlib
            `pvlib.solarposition.get_solarposition(times, latitude, longitude, **kwargs)`
            
            #### Algoritmo
            - **Metodo default**: NREL SPA (Solar Position Algorithm)
            - **Accuratezza**: ±0.0003° per periodo 2000-6000 CE
            - **Riferimento**: Reda, I. and Andreas, A. (2004). Solar position algorithm for solar radiation applications. Solar Energy, 76(5), 577-589.
            
            #### Output DataFrame
            Colonne restituite per ogni timestamp:
            - `elevation` [°]: altezza angolare del sole sopra l'orizzonte (0° = orizzonte, 90° = zenit)
            - `azimuth` [°]: angolo di orientamento del sole (0° = Nord, 90° = Est, 180° = Sud, 270° = Ovest)
            - `zenith` [°]: angolo zenitale (90° - elevation)
            - `apparent_zenith` [°]: zenith corretto per rifrazione atmosferica
            - `apparent_elevation` [°]: elevation corretto per rifrazione
            
            #### Implementazione
            ```python
            def calculate_solar_position(times: pd.DatetimeIndex, lat: float, lon: float) -> pd.DataFrame:
                return pvlib.solarposition.get_solarposition(times, lat, lon)
            
            # Uso
            solpos = calculate_solar_position(times, params["lat"], params["lon"])
            ```
            
            **Nota**: l'elevation negativa indica che il sole è sotto l'orizzonte (notte). Questi valori sono esclusi dai calcoli di irradianza.
            
            ---
            
            ### 3.2 Irradianza Cielo Sereno
            
            #### Modello Ineichen Clear Sky
            Stima l'irradianza solare in condizioni di cielo sereno (assenza di nubi).
            
            #### Funzione pvlib
            `pvlib.location.Location(lat, lon, tz).get_clearsky(times, model='ineichen')`
            
            #### Componenti Irradianza
            Il modello restituisce tre componenti fondamentali:
            
            1. **GHI** (Global Horizontal Irradiance) [W/m²]:
               - Radiazione totale su superficie orizzontale
               - Include componente diretta + diffusa
               - Formula: $GHI = DNI \cdot \cos(\theta_z) + DHI$
            
            2. **DNI** (Direct Normal Irradiance) [W/m²]:
               - Radiazione diretta perpendicolare ai raggi solari
               - Massima quando il sole è perpendicolare alla superficie
            
            3. **DHI** (Diffuse Horizontal Irradiance) [W/m²]:
               - Radiazione diffusa dall'atmosfera su superficie orizzontale
               - Non dipende dall'angolo solare diretto
            
            #### Parametri del Modello
            Il modello Ineichen utilizza:
            - **Linke Turbidity**: torbidità atmosferica (lookup automatico da database pvlib)
            - **Altitude**: altitudine del sito (default 0 m se non specificata)
            - **Airmass**: massa d'aria relativa attraversata dai raggi solari
            
            #### Implementazione
            ```python
            def calculate_clearsky_irradiance(times: pd.DatetimeIndex, lat: float, 
                                              lon: float, tz: str) -> pd.DataFrame:
                site = pvlib.location.Location(lat, lon, tz=tz)
                return site.get_clearsky(times, model="ineichen")
            
            # Uso
            clearsky = calculate_clearsky_irradiance(times, params["lat"], 
                                                     params["lon"], str(params["timezone"]))
            # clearsky.columns: ['ghi', 'dni', 'dhi']
            ```
            
            #### Riferimenti
            - Ineichen, P. and Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.
            
            **Limitazione**: il modello assume cielo sereno. Per dati reali con nuvolosità, occorre utilizzare dati satellitari o stazioni meteorologiche.
            
            ---
            
            ### 3.3 POA Global (Plane of Array Irradiance)
            
            #### Definizione
            POA è l'irradianza totale incidente sul piano inclinato del pannello fotovoltaico, sommando tre contributi:
            
            $$POA_{global} = POA_{direct} + POA_{diffuse} + POA_{reflected}$$
            
            #### Funzione pvlib
            `pvlib.irradiance.get_total_irradiance(surface_tilt, surface_azimuth, dni, ghi, dhi, solar_zenith, solar_azimuth, albedo, **kwargs)`
            
            #### Modelli di Trasposizione
            
            **1. Componente Diretta**:
            $$POA_{direct} = DNI \cdot \cos(\theta)$$
            
            dove $\theta$ è l'angolo di incidenza tra raggio solare e normale al pannello.
            
            **2. Componente Diffusa** (Modello Perez):
            - Suddivide il cielo in regioni circumsolari, orizzonte, e isotropica
            - Riferimento: Perez et al. (1990)
            
            **3. Componente Riflessa**:
            $$POA_{reflected} = GHI \cdot \rho \cdot \frac{1 - \cos(\beta)}{2}$$
            
            dove:
            - $\rho$ = albedo del suolo
            - $\beta$ = tilt del pannello
            - Il fattore $(1 - \cos(\beta))/2$ rappresenta la frazione di vista del suolo dal pannello
            
            #### Implementazione
            ```python
            def calculate_poa_global(clearsky: pd.DataFrame, solpos: pd.DataFrame, 
                                     tilt: float, azimuth: float, albedo: float) -> pd.Series:
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
                return poa['poa_global'].round(0).astype(int)
            
            # Uso
            poa_global = calculate_poa_global(clearsky, solpos, params["tilt_pannello"], 
                                              params["azimuth_pannello"], params["albedo"])
            ```
            
            #### Riferimenti
            - Perez, R., Ineichen, P., Seals, R., Michalsky, J., and Stewart, R. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. Solar Energy, 44(5), 271-289.
            
            **Nota**: l'output `poa_global` è arrotondato a intero per semplicità di visualizzazione.
            
            ---
            
            ### 3.4 Temperatura Ambiente Stimata
            
            #### Modello Sinusoidale Empirico
            In assenza di dati meteorologici reali, la temperatura ambiente è stimata con andamento sinusoidale giornaliero.
            
            #### Formula Generale
            
            $$T_{amb}(h) = T_{media} + \Delta T \cdot \sin\left(\frac{\pi(h-6)}{12}\right)$$
            
            dove:
            - $T_{media}$ = temperatura media giornaliera stagionale [°C]
            - $\Delta T$ = ampiezza escursione termica giornaliera [°C]
            - $h$ = ora del giorno (0-23)
            - Minimo termico: ore 6:00
            - Massimo termico: ore 14:00 (offset +8h dal minimo → 6 + 8 = 14)
            
            #### Parametrizzazione Stagionale
            I parametri $T_{media}$ e $\Delta T$ sono stimati in base a:
            - Mese della simulazione
            - Latitudine del sito
            
            **Correzione latitudinale**: temperature più basse alle latitudini maggiori.
            
            #### Stagioni e Parametri
            
            | Stagione | Mesi | $T_{media}$ | $\Delta T$ |
            |----------|------|-------------|------------|
            | Inverno  | 12, 1, 2 | $8 - (lat - 40) \times 0.5$ | 6°C |
            | Primavera | 3, 4, 5 | $15 - (lat - 40) \times 0.3$ | 8°C |
            | Estate   | 6, 7, 8 | $26 - (lat - 40) \times 0.4$ | 10°C |
            | Autunno  | 9, 10, 11 | $16 - (lat - 40) \times 0.3$ | 7°C |
            
            #### Implementazione
            ```python
            def estimate_ambient_temperature(times: pd.DatetimeIndex, lat: float) -> pd.Series:
                month = times[0].month
                
                # Parametrizzazione stagionale
                if month in [12, 1, 2]:      # Inverno
                    T_media = 8 - (lat - 40) * 0.5
                    escursione = 6
                elif month in [3, 4, 5]:     # Primavera
                    T_media = 15 - (lat - 40) * 0.3
                    escursione = 8
                elif month in [6, 7, 8]:     # Estate
                    T_media = 26 - (lat - 40) * 0.4
                    escursione = 10
                else:                        # Autunno
                    T_media = 16 - (lat - 40) * 0.3
                    escursione = 7
                
                # Andamento sinusoidale (minimo h6, massimo h14)
                hours = times.hour
                T_amb = T_media + escursione * pd.Series(
                    [math.sin(math.pi * (h - 6) / 12) for h in hours],
                    index=times
                )
                
                return T_amb
            ```
            
            **Esempio numerico** (Roma, lat=41.9°, luglio):
            - $T_{media} = 26 - (41.9 - 40) \times 0.4 = 26 - 0.76 = 25.24°C$
            - $\Delta T = 10°C$
            - Ore 6:00: $T = 25.24 + 10 \times \sin(0) = 25.24°C$
            - Ore 14:00: $T = 25.24 + 10 \times \sin(\pi) = 25.24 + 10 = 35.24°C$
            - Ore 22:00: $T = 25.24 + 10 \times \sin(4\pi/3) \approx 25.24 - 8.66 = 16.58°C$
            
            **Limitazione**: stima semplificata, non considera fenomeni meteorologici reali (fronti, venti, nuvolosità). Per analisi dettagliate, utilizzare dati TMY (Typical Meteorological Year).
            """)
        
        with tab4:
            st.markdown("""
            ## 4. CALCOLI PRODUZIONE ELETTRICA
            **Modulo**: `calculations.py`  
            **Funzione**: `calculate_pv_production(params, poa_global, T_amb)`
            
            ---
            
            ### 4.1 Temperatura Celle Fotovoltaiche
            
            #### Modello NOCT
            La temperatura delle celle fotovoltaiche è superiore alla temperatura ambiente a causa dell'assorbimento di radiazione solare. Il modello NOCT (Nominal Operating Cell Temperature) fornisce una stima lineare.
            
            #### Formula Teorica
            
            $$T_{cell} = T_{amb} + \frac{POA}{800} \cdot (NOCT - 20)$$
            
            dove:
            - $T_{cell}$ = temperatura celle [°C]
            - $T_{amb}$ = temperatura ambiente [°C]
            - $POA$ = irradianza sul piano pannello [W/m²]
            - $NOCT$ = temperatura nominale operativa celle [°C]
            - 800 W/m² = irraggiamento di riferimento per NOCT
            - 20°C = temperatura ambiente di riferimento per NOCT
            
            #### Derivazione
            Il modello assume che il sovratemperatura delle celle sia proporzionale all'irraggiamento:
            
            $$\Delta T = T_{cell} - T_{amb} = k \cdot POA$$
            
            Il coefficiente $k$ è calibrato in modo che con $POA = 800$ W/m² e $T_{amb} = 20°C$, si abbia $T_{cell} = NOCT$:
            
            $k = \frac{NOCT - 20}{800}$
            
            #### Implementazione
            ```python
            T_cell = T_amb + (poa_global / 800) * (params["noct"] - 20)
            ```
            
            **Esempio numerico** (NOCT=45°C, T_amb=30°C, POA=1000 W/m²):
            
            $T_{cell} = 30 + \frac{1000}{800} \cdot (45 - 20) = 30 + 1.25 \times 25 = 61.25°C$
            
            #### Riferimenti
            - King, D.L., Boyson, W.E., and Kratochvil, J.A. (2004). Photovoltaic array performance model. Sandia National Laboratories Report SAND2004-3535.
            
            **Nota**: questo modello semplificato non considera effetti di ventilazione, tipo di montaggio, o condizioni di open circuit vs. massima potenza. Per analisi dettagliate, utilizzare modelli Sandia o PVsyst.
            
            ---
            
            ### 4.2 Efficienza Corretta per Temperatura
            
            #### Dipendenza dalla Temperatura
            L'efficienza dei moduli fotovoltaici al silicio cristallino diminuisce all'aumentare della temperatura delle celle. Questo effetto è quantificato dal coefficiente di temperatura.
            
            #### Formula Teorica
            
            $\eta_{corr} = \eta_{nom} \cdot [1 + \gamma \cdot (T_{cell} - 25)]$
            
            dove:
            - $\eta_{corr}$ = efficienza corretta [frazione]
            - $\eta_{nom}$ = efficienza nominale a 25°C [frazione]
            - $\gamma$ = coefficiente di temperatura [1/°C], tipicamente negativo
            - $T_{cell}$ = temperatura celle [°C]
            - 25°C = temperatura di riferimento STC (Standard Test Conditions)
            
            #### Interpretazione Fisica
            - $T_{cell} > 25°C$ → $\eta_{corr} < \eta_{nom}$ (perdita di efficienza)
            - $T_{cell} < 25°C$ → $\eta_{corr} > \eta_{nom}$ (guadagno di efficienza)
            
            #### Implementazione
            ```python
            eff_corr = params["eff"] * (1 + params["temp_coeff"] * (T_cell - 25))
            ```
            
            **Esempio numerico** (η_nom=20%, γ=-0.4%/°C, T_cell=60°C):
            
            $\eta_{corr} = 0.20 \times [1 + (-0.004) \times (60 - 25)]$
            $= 0.20 \times [1 - 0.14] = 0.20 \times 0.86 = 0.172 = 17.2\%$
            
            Perdita: $(20 - 17.2)/20 \times 100 = 14\%$ rispetto all'efficienza nominale.
            
            #### Valori Tipici Coefficiente γ
            - **Silicio monocristallino**: -0.40% a -0.45% per °C
            - **Silicio policristallino**: -0.40% a -0.50% per °C
            - **Film sottile (CdTe)**: -0.25% per °C
            - **Film sottile (a-Si)**: -0.20% per °C
            
            #### Riferimenti
            - IEC 61215: Standard internazionale per test prestazioni moduli fotovoltaici
            
            ---
            
            ### 4.3 Potenza Elettrica Istantanea
            
            #### Formula Generale
            La potenza elettrica DC prodotta da un pannello fotovoltaico è data da:
            
            $P = POA \cdot A \cdot \eta_{corr} \cdot (1 - L)$
            
            dove:
            - $P$ = potenza elettrica DC [W]
            - $POA$ = irradianza piano pannello [W/m²]
            - $A$ = area pannello [m²]
            - $\eta_{corr}$ = efficienza corretta per temperatura [frazione]
            - $L$ = perdite di sistema [frazione]
            
            #### Perdite di Sistema
            Il fattore $(1 - L)$ include:
            - **Perdite ohmiche**: resistenza cavi DC e AC
            - **Perdite inverter**: conversione DC → AC (tipicamente 2-5%)
            - **Mismatch**: differenze tra pannelli (1-3%)
            - **Sporcizia**: deposito polvere, polline (2-5%)
            - **Ombreggiamenti**: eventuali ostacoli (variabile)
            - **Degrado**: riduzione prestazioni nel tempo (~0.5%/anno)
            
            #### Implementazione
            ```python
            # Potenza singolo pannello [W]
            power_single_W = (poa_global * params["area_pannello"] * eff_corr * 
                              (1 - params["losses"])).round(0).astype(int)
            
            # Potenza totale impianto [W]
            power_total_W = power_single_W * params["num_panels_total"]
            ```
            
            **Esempio numerico** (POA=1000 W/m², A=5 m², η_corr=17.2%, L=10%):
            
            $P = 1000 \times 5 \times 0.172 \times 0.90 = 774 \, W$
            
            **Nota**: l'output è arrotondato a intero per semplicità. I valori orari sono Series pandas con index temporale.
            
            ---
            
            ### 4.4 Energia Giornaliera
            
            #### Integrazione Temporale
            L'energia prodotta in un giorno è la somma delle potenze orarie (integrazione numerica con passo 1 ora):
            
            $E_{day} = \sum_{h=0}^{23} P_h \cdot \Delta t = \sum_{h=0}^{23} P_h \cdot 1 \, h \quad [Wh]$
            
            #### Implementazione
            ```python
            # Energia singolo pannello [Wh]
            energy_single_Wh = power_single_W.sum()
            
            # Energia totale impianto [Wh]
            energy_total_Wh = power_total_W.sum()
            
            # Energia per metro quadro di pannello [Wh/m²]
            energy_total_Wh_m2 = energy_total_Wh / (params["area_pannello"] * 
                                                     params["num_panels_total"])
            ```
            
            #### Conversione Unità
            - **Wh → kWh**: dividere per 1000
            - **Wh → MWh**: dividere per 1,000,000
            - **Wh/m²/giorno → kWh/m²/anno**: moltiplicare per 365/1000
            
            **Esempio numerico** (potenza media 500 W per 10 ore effettive):
            
            $E_{day} = 500 \times 10 = 5000 \, Wh = 5 \, kWh$
            
            #### Temperatura Media Celle
            Calcolata come media aritmetica delle 24 temperature orarie:
            
            ```python
            T_cell_avg = T_cell.mean()
            ```
            
            ---
            
            ### 4.5 Assemblaggio Risultati
            
            La funzione `calculate_pv_production()` restituisce un dizionario con:
            
            ```python
            return {
                "power_single_W": power_single_W,        # Serie pandas [W]
                "power_total_W": power_total_W,          # Serie pandas [W]
                "energy_single_Wh": energy_single,       # Scalare [Wh]
                "energy_total_Wh": energy_total,         # Scalare [Wh]
                "energy_total_Wh_m2": energy_total_m2,   # Scalare [Wh/m²]
                "T_cell_avg": T_cell.mean()              # Scalare [°C]
            }
            ```
            
            **Nota**: le serie temporali mantengono l'index DatetimeIndex per sincronizzazione con grafici e analisi successive.
            """)