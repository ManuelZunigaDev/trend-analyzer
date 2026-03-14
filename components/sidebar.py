import streamlit as st
 
 
 
TIMEFRAME_MAP = {
    "Últimos 7 días":  "now 7-d",
    "Último mes":      "today 1-m",
    "Últimos 3 meses": "today 3-m",
    "Último año":      "today 12-m",
    "Últimos 5 años":  "today 5-y",


}
 
GEO_MAP = {
    "Mundial": "",
    "México":  "MX",
    "USA":     "US",
    "España":  "ES",
    "Argentina": "AR",
    "Colombia":  "CO",
}
 
 
def render_sidebar() -> dict:
    """

    Renderiza el sidebar y retorna los parámetros seleccionados por el usuario.
 
    Returns:
        Dict con: keywords (list), timeframe (str), timeframe_label (str),
                  geo (str), horizon (int), show_table (bool), show_related (bool).
    """
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        st.markdown("---")
 
        raw_input = st.text_input(
            "Palabras clave",
            placeholder="ej. bitcoin, ethereum",
            help="Separa varias palabras con comas (máx. 5)",
        )
 
        timeframe_label = st.selectbox("Período", list(TIMEFRAME_MAP.keys()), index=3)
        timeframe       = TIMEFRAME_MAP[timeframe_label]
 
        geo_label = st.selectbox("Región", list(GEO_MAP.keys()), index=1)
        geo       = GEO_MAP[geo_label]
 
        horizon    = st.slider("Semanas a predecir", 4, 52, 12)
        show_table   = st.checkbox("Mostrar tabla de datos", value=False)
        show_related = st.checkbox("Mostrar búsquedas relacionadas", value=False)
 
        st.markdown("---")
        st.markdown(
            "<div style='color:#4b5563;font-size:0.72rem;line-height:1.8'>"
            "Datos: Google Trends · pytrends<br>"
            "Predicción: Meta Prophet<br>"
            "Caché: 1 hora<br>"
            "Exportación: CSV · Excel</div>",

            # fmt: off
            unsafe_allow_html=True,
        )
 


    keywords = [k.strip() for k in raw_input.split(",") if k.strip()][:5]
 
    return dict(
        keywords=keywords,
        timeframe=timeframe,
        timeframe_label=timeframe_label,
        geo=geo,
        horizon=horizon,
        show_table=show_table,
        show_related=show_related,
    )


