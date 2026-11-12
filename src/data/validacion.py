"""Validación de esquema y reporte de calidad."""
import pandas as pd

COLUMNAS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def validar_esquema(df):
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Columnas faltantes: {faltan}")


def reporte_calidad(df: pd.DataFrame) -> dict:
    validar_esquema(df)
    return {
        "filas": int(len(df)),
        "columnas": int(df.shape[1]),
        "fecha_min": str(df.InvoiceDate.min()),
        "fecha_max": str(df.InvoiceDate.max()),
        "clientes_unicos": int(df.CustomerID.nunique()),
        "facturas_unicas": int(df.InvoiceNo.nunique()),
        "productos_unicos": int(df.StockCode.nunique()),
        "paises": int(df.Country.nunique()),
        "nulos": {c: int(v) for c, v in df.isna().sum().items()},
        "duplicados_exactos": int(df.duplicated().sum()),
        "cancelaciones": int(df.InvoiceNo.astype(str).str.upper().str.startswith("C").sum()),
        "cantidad_no_positiva": int((df.Quantity <= 0).sum()),
        "precio_no_positivo": int((df.UnitPrice <= 0).sum()),
    }
