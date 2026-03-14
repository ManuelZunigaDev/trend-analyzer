import streamlit as st
 
COLORS = ["#6c7aff", "#f472b6", "#34d399", "#fbbf24", "#f87171"]
 
 
def tag_html(kw: str, idx: int) -> str:
    """Genera un badge HTML con color único para cada keyword."""
    c = COLORS[idx % len(COLORS)]
    return f'<span class="kw-tag" style="background:{c}22;color:{c};border:1px solid {c}44">{kw}</span>'
 
 
def render_metric_cards(data, available_kws: list, metrics_data: dict) -> None:
    """
    Renderiza una fila de tarjetas con las métricas de cada keyword.
 
    Args:
        data:          DataFrame histórico.
        available_kws: Keywords disponibles en el DataFrame.
        metrics_data:  Dict {kw: metrics_dict} calculado previamente.
    """
    cols = st.columns(len(available_kws))
    for i, kw in enumerate(available_kws):
        m      = metrics_data[kw]
        accent = COLORS[i % len(COLORS)]
        delta_class = "delta-up" if m["delta"] > 0 else ("delta-down" if m["delta"] < 0 else "delta-flat")
        delta_icon  = "▲" if m["delta"] > 0 else ("▼" if m["delta"] < 0 else "→")
 
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
              <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{accent}"></div>
              <div class="metric-label">{kw}</div>
              <div class="metric-value">{m['current']}</div>
              <div class="metric-delta {delta_class}">{delta_icon} {abs(m['delta'])} vs 5 sem. atrás</div>
              <div style="margin-top:.6rem;font-size:.75rem;color:#6b7280">
                Pico: <b style="color:#e8e8f0">{m['peak']}</b> &nbsp;|&nbsp;
                Promedio: <b style="color:#e8e8f0">{m['avg']}</b> &nbsp;|&nbsp;
                Score: <b style="color:{accent}">{m['score']}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)