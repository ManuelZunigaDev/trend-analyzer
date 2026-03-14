import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
 
 
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends(keywords: list, timeframe: str, geo: str) -> pd.DataFrame:
    """
    Descarga datos de Google Trends vía pytrends.
 
    Args:
        keywords:  Lista de hasta 5 términos de búsqueda.
        timeframe: Período en formato pytrends (ej. 'today 12-m').
        geo:       Código de país ISO 3166-1 (ej. 'MX', 'US'). '' = mundial.
 
    Returns:
        DataFrame con una columna por keyword y el índice como fecha.
    """
    pytrends = TrendReq(hl="es-MX", tz=360)
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    data = pytrends.interest_over_time()
 
    if data.empty:
        return pd.DataFrame()
 
    if "isPartial" in data.columns:
        data = data.drop(columns=["isPartial"])
 
    return data
 

 
 
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_related_queries(keyword: str, geo: str) -> dict:
    """
    Obtiene las búsquedas relacionadas (top y rising) para una keyword.
 
    Returns:
        Dict con claves 'top' y 'rising', cada una un DataFrame o None.
    """
    pytrends = TrendReq(hl="es-MX", tz=360)
    pytrends.build_payload([keyword], geo=geo)
    related = pytrends.related_queries()
    return {
        "top":   related.get(keyword, {}).get("top"),
        "rising": related.get(keyword, {}).get("rising"),
    }
 