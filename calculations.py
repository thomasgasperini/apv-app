import pandas as pd
import pvlib

def calculate_pv(params):
    times = pd.date_range(
        start=pd.Timestamp(params["data"]),
        end=pd.Timestamp(params["data"]) + pd.Timedelta(days=1) - pd.Timedelta(hours=1),
        freq="1h",
        tz=params["timezone"]
    )

    # Posizione solare
    solpos = pvlib.solarposition.get_solarposition(times, params["lat"], params["lon"])

    # Cielo sereno
    site = pvlib.location.Location(params["lat"], params["lon"], tz=params["timezone"])
    clearsky = site.get_clearsky(times, model="ineichen")

    # Irradianza su pannello
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=params["tilt"],
        surface_azimuth=params["azimuth"],
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth'],
        albedo=params["albedo"]
    )

    # Temperatura cella
    T_cell = 25 + (params["noct"] - 20) / 800 * poa['poa_global']

    # Potenza
    P_dc = poa['poa_global'] * params["area"] * params["eff"] * (1 + params["temp_coeff"]*(T_cell-25))
    P_ac = P_dc * (1 - params["losses"])
    E_day = P_ac.sum() / 1000

    return {
        "times": times,
        "solpos": solpos,
        "clearsky": clearsky,
        "poa": poa,
        "T_cell": T_cell,
        "P_dc": P_dc,
        "P_ac": P_ac,
        "E_day": E_day
    }
