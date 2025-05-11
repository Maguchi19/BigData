# utils/forecasting.py

import pandas as pd
from prophet import Prophet

def generar_pronostico(df, col_objetivo, meses_a_pronosticar=12):
    """
    Genera un pronóstico para una serie temporal usando Prophet.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'ds' (fechas) y la columna objetivo.
        col_objetivo (str): Nombre de la columna a predecir (usualmente 'y').
        meses_a_pronosticar (int): Número de meses a pronosticar.

    Returns:
        pd.DataFrame: DataFrame con predicciones y límites de confianza.
    """
    df = df[["ds", col_objetivo]].rename(columns={col_objetivo: "y"})
    df = df.sort_values("ds")

    modelo = Prophet()
    modelo.fit(df)

    futuro = modelo.make_future_dataframe(periods=meses_a_pronosticar, freq='MS')
    pronostico = modelo.predict(futuro)

    return pronostico[["ds", "yhat", "yhat_lower", "yhat_upper"]]
