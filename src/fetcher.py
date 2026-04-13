import streamlit as st
import pandas as pd
import time
import random
from pytrends.request import TrendReq

# ── Configuración de Reintentos
MAX_RETRIES = 5
BASE_DELAY = 5  # Segundos para exponencial backoff

# Headers para simular navegador real y mitigar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def get_pytrends_instance():
    """Crea una instancia de pytrends con headers aleatorios."""
    return TrendReq(
        hl="es-MX", 
        tz=360, 
        timeout=(10, 25),
        requests_args={
            'headers': {
                'User-Agent': random.choice(USER_AGENTS)
            }
        }
    )

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends(keywords: list, timeframe: str, geo: str) -> pd.DataFrame:
    """
    Descarga datos de Google Trends con manejo de errores, reintentos y control de flujo.
    
    NOTA: pytrends realiza solicitudes no oficiales (scraping). 
    Para entornos de producción con alta carga, se recomienda la API oficial de Google Ads.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Control de flujo: sleep preventivo aleatorio
            time.sleep(random.uniform(1.5, 3.5))
            
            pytrends = get_pytrends_instance()
            pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
            data = pytrends.interest_over_time()

            if data.empty:
                return pd.DataFrame()

            if "isPartial" in data.columns:
                data = data.drop(columns=["isPartial"])

            return data

        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "too many requests" in msg:
                retries += 1
                wait_time = BASE_DELAY * (2 ** retries) + random.uniform(2, 6)
                st.warning(f"⚠️ Google reportó exceso de peticiones (429). Reintentando en {wait_time:.1f}s... ({retries}/{MAX_RETRIES})")
                time.sleep(wait_time)
            else:
                st.error(f"❌ Error al consultar Google Trends: {e}")
                break
    
    return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_related_queries(keyword: str, geo: str) -> dict:
    """
    Obtiene búsquedas relacionadas con gestión de rate limit.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            time.sleep(random.uniform(1.0, 3.0))
            pytrends = get_pytrends_instance()
            pytrends.build_payload([keyword], geo=geo)
            related = pytrends.related_queries()
            
            if not related:
                return {"top": None, "rising": None}
                
            return {
                "top":   related.get(keyword, {}).get("top"),
                "rising": related.get(keyword, {}).get("rising"),
            }
        except Exception as e:
            if "429" in str(e):
                retries += 1
                time.sleep(BASE_DELAY * (2 ** retries))
            else:
                break
                
    return {"top": None, "rising": None}