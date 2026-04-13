import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 

COLORS = ["#6c7aff", "#f472b6", "#34d399", "#fbbf24", "#f87171"]
 
 

def _theme() -> dict:
    """Devuelve el dict de layout compartido para todos los gráficos."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af"),
        xaxis=dict(gridcolor="#1e2235", zeroline=False),
        yaxis=dict(gridcolor="#1e2235", zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2235", borderwidth=1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
 
 
def render_historical(data: pd.DataFrame, available_kws: list, timeframe_label: str) -> None:
    """Gráfica de línea multi-keyword con área rellena."""
    fig = go.Figure()
    for i, kw in enumerate(available_kws):
        color = COLORS[i % len(COLORS)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Scatter(
            x=data.index, y=data[kw], name=kw,
            mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.06)",
            hovertemplate=f"<b>{kw}</b><br>%{{x|%d %b %Y}}<br>Interés: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text=f"Interés a lo largo del tiempo · {timeframe_label}",
                   font=dict(family="Syne", size=15, color="#e8e8f0")),
        hovermode="x unified", height=380, **_theme(),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
 
def render_forecast(kw: str, data: pd.DataFrame, fc: pd.DataFrame,
                    color: str, changepoints: list) -> None:
    """
    Gráfica de predicción con banda de confianza y anotaciones
    de puntos de cambio de tendencia.
    """
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    hist_end  = str(data.index[-1])
    fc_future = fc[fc["ds"] > pd.Timestamp(hist_end)]
 
    fig = go.Figure()
 
    fig.add_trace(go.Scatter(
        x=data.index, y=data[kw], name="Histórico",
        mode="lines", line=dict(color=color, width=2),
    ))
 
    fig.add_trace(go.Scatter(
        x=pd.concat([fc_future["ds"], fc_future["ds"].iloc[::-1]]),
        y=pd.concat([fc_future["yhat_upper"], fc_future["yhat_lower"].iloc[::-1]]),
        fill="toself", fillcolor=f"rgba({r},{g},{b},0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Intervalo 80%", hoverinfo="skip",
    ))
 
    fig.add_trace(go.Scatter(
        x=fc_future["ds"], y=fc_future["yhat"], name="Predicción",
        mode="lines", line=dict(color=color, width=2.5, dash="dot"),
        hovertemplate=f"<b>{kw} (pred.)</b><br>%{{x|%d %b %Y}}<br>Estimado: %{{y:.1f}}<extra></extra>",
    ))
 
    fig.add_vline(x=hist_end, line_width=1, line_dash="dash", line_color="#4b5563")
    fig.add_annotation(
        x=hist_end, y=1.02, yref="paper",
        text="Hoy", showarrow=False,
        font=dict(color="#9ca3af"),
        xanchor="center", yanchor="bottom"
    )
 
    for cp in changepoints:
        icon  = "▲" if cp["direction"] == "up" else "▼"
        clr   = "#34d399" if cp["direction"] == "up" else "#f87171"
        fig.add_vline(x=cp["date"], line_width=1, line_dash="dot", line_color=clr)
        fig.add_annotation(
            x=cp["date"], y=0.98, yref="paper",
            text=icon, showarrow=False,
            font=dict(color=clr, size=14),
            xanchor="left", yanchor="top"
        )
 
    fig.update_layout(
        title=dict(text=f"<b>{kw}</b> · predicción con intervalos de confianza",
                   font=dict(family="Syne", size=14, color="#e8e8f0")),
        height=320, hovermode="x unified", **_theme(),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
 
def render_radar(available_kws: list, metrics_data: dict) -> None:
    """Radar chart de comparación entre keywords (solo si hay más de una)."""
    if len(available_kws) < 2:
        return
    categories = ["Valor actual", "Pico", "Promedio", "Score"]
    fig = go.Figure()
    for i, kw in enumerate(available_kws):
        m     = metrics_data[kw]
        color = COLORS[i % len(COLORS)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Scatterpolar(
            r=[m["current"], m["peak"], m["avg"], m["score"]],
            theta=categories, fill="toself", name=kw,
            line=dict(color=color, width=2),
            fillcolor=f"rgba({r},{g},{b},0.10)",
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="#1e2235", color="#6b7280"),
            angularaxis=dict(gridcolor="#1e2235", color="#9ca3af"),
        ),
        height=400, **_theme(),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
 
def render_correlation_heatmap(corr_matrix: pd.DataFrame) -> None:
    """Heatmap de correlación de Pearson entre keywords."""
    fig = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0, "#1a1e30"], [0.5, "#6c7aff"], [1, "#f472b6"]],
        zmin=-1, zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        hovertemplate="(%{x}, %{y})<br>r = %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(height=340, **_theme())
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)