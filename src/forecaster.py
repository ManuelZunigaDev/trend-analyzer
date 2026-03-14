import pandas as pd
from prophet import Prophet
import logging
 
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
 
 
def run_prophet(series: pd.Series, horizon: int) -> pd.DataFrame:
    """
    Entrena un modelo Prophet y genera predicciones futuras.
 
    Args:
        series:  Serie temporal indexada por fecha (salida de fetch_trends).
        horizon: Número de semanas futuras a predecir.
 
    Returns:
        DataFrame de Prophet con columnas ds, yhat, yhat_lower, yhat_upper,
        trend, y los componentes estacionales.
    """
    df = series.reset_index()
    df.columns = ["ds", "y"]
    df["ds"] = pd.to_datetime(df["ds"])
 
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.3,   
        seasonality_prior_scale=10.0,
        interval_width=0.80,           
    )
 
    model.fit(df)
 
    future   = model.make_future_dataframe(periods=horizon, freq="W")
    forecast = model.predict(future)
 



    forecast["yhat"]       = forecast["yhat"].clip(lower=0)
    forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
    forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)
 
    return forecast
 
 
def get_changepoints(forecast: pd.DataFrame, series: pd.Series, n: int = 3) -> list[dict]:


    """
    Identifica los N cambios de tendencia más importantes en el histórico.
 
    Returns:
        Lista de dicts con 'date' y 'direction' ('up' | 'down').
    """
    trend = forecast[forecast["ds"] <= series.index.max()][["ds", "trend"]].copy()
    trend["trend_diff"] = trend["trend"].diff()
    trend = trend.dropna()
 
    top = trend.reindex(trend["trend_diff"].abs().nlargest(n).index)
    return [
        {

            
            "date": row["ds"],
            "direction": "up" if row["trend_diff"] > 0 else "down",
        }
        for _, row in top.iterrows()
    ]