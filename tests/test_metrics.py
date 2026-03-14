
import streamlit as st
import pandas as pd
 
st.set_page_config(
    page_title="Trend Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
from components.styles      import inject_css
from components.sidebar     import render_sidebar
from components.metric_cards import render_metric_cards, tag_html, COLORS
from components.charts      import (
    render_historical,
    render_forecast,
    render_radar,
    render_correlation_heatmap,
)
from src.fetcher    import fetch_trends, fetch_related_queries
from src.metrics    import compute_metrics, compute_correlation_matrix
from src.forecaster import run_prophet, get_changepoints
from src.exporter   import to_csv, to_excel
from src.insights   import build_insights_section
 
inject_css()
 
params = render_sidebar()
keywords      = params["keywords"]
timeframe     = params["timeframe"]
timeframe_label = params["timeframe_label"]
geo           = params["geo"]
horizon       = params["horizon"]
show_table    = params["show_table"]
show_related  = params["show_related"]
 
st.markdown("""
<div class="hero">
  <h1>Trend Analyzer</h1>
  <p>Analiza tendencias de búsqueda y predice su crecimiento con IA</p>
</div>
""", unsafe_allow_html=True)
 
if not keywords:

    st.markdown("""
    <div class="empty-state">
      <div style="font-size:3rem;margin-bottom:1rem">📡</div>
      <h3>Escribe una palabra clave para empezar</h3>
      <p>Puedes comparar hasta 5 términos separados por comas</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
 
tags_html = " ".join(tag_html(kw, i) for i, kw in enumerate(keywords))

st.markdown(f"<div style='margin-bottom:1.5rem'>{tags_html}</div>", unsafe_allow_html=True)
 


with st.spinner("Consultando Google Trends…"):
    try:
        data = fetch_trends(tuple(keywords), timeframe, geo)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        st.stop()
 
if data.empty:
    st.warning("No se encontraron datos para estos términos en el período seleccionado.")
    st.stop()
 
available_kws = [k for k in keywords if k in data.columns]
 
metrics_data = {kw: compute_metrics(data[kw]) for kw in available_kws}
 
st.markdown('<div class="section-title">📊 Métricas clave</div>', unsafe_allow_html=True)
render_metric_cards(data, available_kws, metrics_data)
 
st.markdown('<div class="section-title">📈 Tendencia histórica</div>', unsafe_allow_html=True)
render_historical(data, available_kws, timeframe_label)



st.markdown(f'<div class="section-title">🔮 Predicción · próximas {horizon} semanas</div>',
            unsafe_allow_html=True)
 
forecast_dfs = {}
for i, kw in enumerate(available_kws):
    with st.spinner(f"Entrenando modelo para **{kw}**…"):
        try:
            fc = run_prophet(data[kw], horizon)
            forecast_dfs[kw] = fc
        except Exception as e:
            st.warning(f"No se pudo predecir '{kw}': {e}")
            continue
 
    changepoints = get_changepoints(fc, data[kw])
    render_forecast(kw, data, fc, COLORS[i % len(COLORS)], changepoints)
 
if len(available_kws) > 1:

    st.markdown('<div class="section-title">🕸️ Comparación global</div>', unsafe_allow_html=True)
    render_radar(available_kws, metrics_data)
 
if len(available_kws) >= 2:
    st.markdown('<div class="section-title">🔗 Correlación entre keywords</div>',
                unsafe_allow_html=True)
    corr = compute_correlation_matrix(data, available_kws)
    render_correlation_heatmap(corr)


st.markdown('<div class="section-title">💡 Insights automáticos</div>', unsafe_allow_html=True)
bullets = build_insights_section(data, available_kws, forecast_dfs, horizon)
for bullet in bullets:
    st.markdown(f'<div class="insight-box">{bullet}</div>', unsafe_allow_html=True)
 



if show_related and len(available_kws) == 1:
    kw = available_kws[0]
    st.markdown('<div class="section-title">🔍 Búsquedas relacionadas</div>', unsafe_allow_html=True)
    with st.spinner("Cargando búsquedas relacionadas…"):
        related = fetch_related_queries(kw, geo)
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Top búsquedas")
        if related["top"] is not None:
            st.dataframe(related["top"], use_container_width=True, height=200)
    with col2:
        st.caption("En tendencia")
        if related["rising"] is not None:
            st.dataframe(related["rising"], use_container_width=True, height=200)
 
if show_table:
    st.markdown('<div class="section-title">🗂️ Datos históricos</div>', unsafe_allow_html=True)
    st.dataframe(
        data[available_kws].style.background_gradient(cmap="Blues", axis=0),
        use_container_width=True, height=300,
    )




st.markdown('<div class="section-title">⬇️ Exportar datos</div>', unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([1, 1, 4])
with col_a:
    st.download_button("📄 CSV", data=to_csv(data, available_kws),
                       file_name="tendencias.csv", mime="text/csv")
with col_b:
    st.download_button("📊 Excel", data=to_excel(data, available_kws),
                       file_name="tendencias.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")