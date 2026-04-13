import pandas as pd
from prophet import Prophet
import logging

logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


def run_prophet(
        series: pd.Series,
        horizon: int
    ) -> pd.DataFrame:
    """
    Entrena un modelo Prophet y genera predicciones futuras.
    """

    # ── Preparar datos
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

    # 🔧 Generar fechas futuras
    future = model.make_future_dataframe(
        periods=horizon,
        freq="W"
    )

    forecast = model.predict(future)

    # 🔧 Evitar valores negativos
    forecast["yhat"] = forecast["yhat"].clip(lower=0)
    forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
    forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

    # 🔧 FORZAR datetime limpio
    forecast["ds"] = pd.to_datetime(
        forecast["ds"]
    ).dt.tz_localize(None)

    return forecast


def get_changepoints(
        forecast: pd.DataFrame,
        series: pd.Series,
        n: int = 3
    ) -> list[dict]:

    """
    Identifica los N cambios de tendencia más importantes.
    """

    # 🔧 Limpiar fechas
    series_end = pd.to_datetime(
        series.index.max()
    ).tz_localize(None)

    forecast["ds"] = pd.to_datetime(
        forecast["ds"]
    ).dt.tz_localize(None)

    # ── Filtrar histórico
    trend = forecast[
        forecast["ds"] <= series_end
    ][["ds", "trend"]].copy()

    trend["trend_diff"] = trend["trend"].diff()

    trend = trend.dropna()

    # ── Tomar los cambios más fuertes
    top = trend.loc[
        trend["trend_diff"]
        .abs()
        .nlargest(n)
        .index
    ]

    # 🔧 Convertir fechas a string (MUY IMPORTANTE)
    changepoints = []

    for _, row in top.iterrows():

        changepoints.append({
            "date": str(row["ds"]),
            "direction": (
                "up"
                if row["trend_diff"] > 0
                else "down"
            )
        })

    return changepoints