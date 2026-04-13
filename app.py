
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# ── Config (debe ir antes de cualquier otro st.*)
st.set_page_config(
    page_title="Trend Analyzer",
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
 
# ── CSS global
inject_css()
 
# ── Sidebar → parámetros
params = render_sidebar()
keywords      = params["keywords"]
timeframe     = params["timeframe"]
timeframe_label = params["timeframe_label"]
geo           = params["geo"]
horizon       = params["horizon"]
show_table    = params["show_table"]
show_related  = params["show_related"]
 
# ── Hero
st.markdown("""
<div class="hero">
  <h1>Trend Analyzer Pro</h1>
  <p>Análisis predictivo de tendencias con Inteligencia Artificial</p>
</div>
""", unsafe_allow_html=True)
 
# ── Navegación Principal (streamlit-option-menu)
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Insights", "Exportar"],
    icons=["speedometer2", "lightbulb", "cloud-download"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "#6c7aff", "font-size": "18px"}, 
        "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#262b45"},
        "nav-link-selected": {"background-color": "#6c7aff", "color": "white"},
    }
)

# ── Empty state
if not keywords:
    st.markdown("""
    <div class="empty-state">
      <div style="font-size:3rem;margin-bottom:1rem;color:#6c7aff">📡</div>
      <h3>Escribe una palabra clave para empezar</h3>
      <p>Puedes comparar hasta 5 términos en el panel lateral para ver análisis predictivos</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
 
# ── Tags de keywords
tags_html = " ".join(tag_html(kw, i) for i, kw in enumerate(keywords))
st.markdown(f"<div style='margin-bottom:1.5rem'>{tags_html}</div>", unsafe_allow_html=True)
 
# ── Fetch datos con manejo de errores (ya incluido en fetcher.py)
with st.spinner("Conectando con Google Trends..."):
    data = fetch_trends(tuple(keywords), timeframe, geo)
 
if data.empty:
    st.warning("No se pudieron obtener datos. Google puede estar limitando las peticiones temporalmente (Error 429). Por favor, intenta de nuevo en unos minutos.")
    st.stop()
 
available_kws = [k for k in keywords if k in data.columns]
 
# ── Sección: Dashboard
if selected == "Dashboard":
    # Métricas
    st.markdown('<div class="section-title">Metricas Clave</div>', unsafe_allow_html=True)
    metrics_data = {kw: compute_metrics(data[kw]) for kw in available_kws}
    render_metric_cards(data, available_kws, metrics_data)
     
    # Gráfica histórica
    st.markdown('<div class="section-title">Tendencia Historica</div>', unsafe_allow_html=True)
    render_historical(data, available_kws, timeframe_label)
     
    # Predicción Prophet
    st.markdown(f'<div class="section-title">Prediccion a {horizon} semanas</div>', unsafe_allow_html=True)
    forecast_dfs = {}
    for i, kw in enumerate(available_kws):
        with st.spinner(f"Entrenando modelo para {kw}..."):
            try:
                fc = run_prophet(data[kw], horizon)
                forecast_dfs[kw] = fc
            except Exception as e:
                st.warning(f"Error en predicción de '{kw}': {e}")
                continue
        changepoints = get_changepoints(fc, data[kw])
        render_forecast(kw, data, fc, COLORS[i % len(COLORS)], changepoints)
     
    # Análisis avanzado (Radar y Correlación)
    if len(available_kws) > 1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Comparacion Global</div>', unsafe_allow_html=True)
            render_radar(available_kws, metrics_data)
        with col2:
            st.markdown('<div class="section-title">Matriz de Correlacion</div>', unsafe_allow_html=True)
            corr = compute_correlation_matrix(data, available_kws)
            render_correlation_heatmap(corr)

    # Búsquedas relacionadas
    if show_related and len(available_kws) == 1:
        kw = available_kws[0]
        st.markdown('<div class="section-title">Busquedas Relacionadas</div>', unsafe_allow_html=True)
        with st.spinner("Cargando datos relacionados..."):
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

    # Tabla de datos
    if show_table:
        st.markdown('<div class="section-title">Datos Crutos</div>', unsafe_allow_html=True)
        st.dataframe(
            data[available_kws].style.background_gradient(cmap="Blues", axis=0),
            use_container_width=True, height=300,
        )

# ── Sección: Insights
elif selected == "Insights":
    st.markdown('<div class="section-title">Insights Generados por IA</div>', unsafe_allow_html=True)
    # Necesitamos calcular forecast si no estamos en la pestaña dashboard
    forecast_dfs = {}
    for i, kw in enumerate(available_kws):
        try:
            fc = run_prophet(data[kw], horizon)
            forecast_dfs[kw] = fc
        except: continue
        
    bullets = build_insights_section(data, available_kws, forecast_dfs, horizon)
    if not bullets:
        st.info("No hay suficientes datos para generar insights en este momento.")
    for bullet in bullets:
        st.markdown(f'<div class="insight-box">{bullet}</div>', unsafe_allow_html=True)

# ── Sección: Exportar
elif selected == "Exportar":
    st.markdown('<div class="section-title">Exportacion de Reportes</div>', unsafe_allow_html=True)
    st.info("Desde aquí puedes descargar los datos históricos procesados en diferentes formatos.")
    
    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        st.download_button("Descargar CSV", data=to_csv(data, available_kws),
                           file_name="tendencias.csv", mime="text/csv")
    with col_b:
        st.download_button("Descargar Excel", data=to_excel(data, available_kws),
                           file_name="tendencias.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
 