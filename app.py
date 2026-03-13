import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from prophet import Prophet

st.title("Trend Analyzer")
st.write("Analiza tendencias de búsqueda y predice su crecimiento")

keyword = st.text_input("Escribe una palabra o tema")

if keyword:

    pytrends = TrendReq()

    pytrends.build_payload([keyword], timeframe="today 12-m")

    data = pytrends.interest_over_time()

    if not data.empty:

        st.subheader("Tendencia histórica")

        fig = px.line(
            data,
            x=data.index,
            y=keyword,
            title=f"Tendencia de {keyword}"
        )

        st.plotly_chart(fig)

        st.subheader("Predicción")

        df = data.reset_index()[["date", keyword]]
        df.columns = ["ds", "y"]

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=30)

        forecast = model.predict(future)

        fig2 = px.line(
            forecast,
            x="ds",
            y="yhat",
            title="Predicción de tendencia"
        )

        st.plotly_chart(fig2)

    else:
        st.write("No se encontraron datos")