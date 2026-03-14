from src.metrics import compute_metrics, generate_insight
 
 
def build_insights_section(data, available_kws: list, forecast_dfs: dict, horizon: int) -> list[str]:
    """
    Genera la lista de bullets de insights para todas las keywords analizadas.
 
    Args:
        data:          DataFrame histórico (salida de fetch_trends).
        available_kws: Keywords presentes en el DataFrame.
        forecast_dfs:  Dict {keyword: forecast_DataFrame} de Prophet.
        horizon:       Semanas predichas.
 
    Returns:
        Lista de strings en markdown, uno por keyword.
    """
    bullets = []
    for kw in available_kws:
        m  = compute_metrics(data[kw])
        fc = forecast_dfs.get(kw)
        forecast_end = float(fc["yhat"].iloc[-1]) if fc is not None else m["current"]
        bullets.append(generate_insight(kw, m, horizon, forecast_end))
    return bullets