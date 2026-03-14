import pandas as pd
from io import BytesIO
 
 
def to_csv(data: pd.DataFrame, keywords: list) -> bytes:
    """Exporta el DataFrame histórico a CSV en memoria."""
    return data[keywords].to_csv().encode("utf-8")
 


def to_excel(data: pd.DataFrame, keywords: list) -> bytes:
    """
    Exporta el DataFrame histórico a Excel con dos hojas:
      - 'Tendencias': datos históricos de interés.
      - 'Resumen':    estadísticas descriptivas por keyword.
    """
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        data[keywords].to_excel(writer, sheet_name="Tendencias", index=True)
        data[keywords].describe().round(2).to_excel(writer, sheet_name="Resumen")
    return buf.getvalue()