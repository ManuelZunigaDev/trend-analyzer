import pandas as pd
import numpy as np
 
 
def compute_metrics(series: pd.Series) -> dict:
    """
    Calcula métricas clave para una serie temporal de interés.
 
    Returns:
        Dict con: current, peak, avg, delta, volatility, momentum, score.
    """
    current  = int(series.iloc[-1])
    previous = int(series.iloc[-5]) if len(series) >= 5 else int(series.iloc[0])
    peak     = int(series.max())
    avg      = round(float(series.mean()), 1)
    delta    = current - previous
 
    volatility = round(float(series.std() / avg * 100), 1) if avg > 0 else 0.0
 
    recent = series.iloc[-8:] if len(series) >= 8 else series
    x = np.arange(len(recent))
    slope = float(np.polyfit(x, recent.values, 1)[0]) if len(recent) > 1 else 0.0
    momentum = round(slope, 2)
 
    growth_score   = min(max((delta / peak * 100) if peak > 0 else 0, -50), 50) + 50
    momentum_score = min(max(momentum * 10, -50), 50) + 50
    level_score    = (current / peak * 100) if peak > 0 else 0
    score = round((growth_score * 0.4 + momentum_score * 0.3 + level_score * 0.3), 1)
 
    return dict(
        current=current,
        peak=peak,
        avg=avg,
        delta=delta,
        volatility=volatility,
        momentum=momentum,
        score=score,
    )
 
def compute_correlation_matrix(data: pd.DataFrame, keywords: list) -> pd.DataFrame:
    """
    Calcula la matriz de correlación de Pearson entre keywords.
 
    Returns:
        DataFrame cuadrado con los coeficientes de correlación.
    """
    return data[keywords].corr(method="pearson").round(2)
 
 
def generate_insight(kw: str, metrics: dict, horizon: int, forecast_end: float) -> str:
    """
    Genera un bullet de insight en lenguaje natural para una keyword.
 
    Args:
        kw:           Nombre de la keyword.
        metrics:      Dict devuelto por compute_metrics().
        horizon:      Semanas hacia adelante que predijo Prophet.
        forecast_end: Valor yhat al final del período de predicción.
 
    Returns:
        String con el insight listo para mostrar en la UI.
    """
    delta_txt = (
        f"subió {metrics['delta']} puntos"   if metrics["delta"] > 0
        else f"bajó {abs(metrics['delta'])} puntos" if metrics["delta"] < 0
        else "se mantuvo estable"
    )
    momentum_txt = (
        "con impulso positivo"  if metrics["momentum"] > 0.5
        else "con impulso negativo" if metrics["momentum"] < -0.5
        else "sin tendencia clara"
    )
    forecast_dir = "crecimiento" if forecast_end > metrics["current"] else "corrección"
 
    return (
        f"**{kw}** {delta_txt} en las últimas 5 semanas {momentum_txt}. "
        f"El modelo predice una {forecast_dir} en las próximas {horizon} semanas "
        f"(score de tendencia: {metrics['score']}/100)."
    )

    