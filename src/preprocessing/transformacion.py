"""Transformaciones: matriz de modelado y agregados exploratorios."""
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from src import config


def preparar_matriz(rfm: pd.DataFrame, features=None):
    """log1p (corrige asimetría) + estandarización. Devuelve (X, scaler)."""
    features = features or config.FEATURES
    scaler = StandardScaler()
    return scaler.fit_transform(np.log1p(rfm[features])), scaler


def agregados_eda(c: pd.DataFrame) -> dict:
    """Tablas pequeñas para el dashboard (evita cargar 400k filas)."""
    mensual = c.groupby(c.InvoiceDate.dt.to_period("M").astype(str)).agg(
        Ingresos=("TotalPrice", "sum"), Facturas=("InvoiceNo", "nunique"), Clientes=("CustomerID", "nunique")).reset_index()
    mensual.columns = ["Mes", "Ingresos", "Facturas", "Clientes"]
    pais = c.groupby("Country").agg(Ingresos=("TotalPrice", "sum"), Clientes=("CustomerID", "nunique"),
                                    Facturas=("InvoiceNo", "nunique")).sort_values("Ingresos", ascending=False).reset_index()
    prod = c.groupby("Description").agg(Ingresos=("TotalPrice", "sum"), Unidades=("Quantity", "sum"),
                                        Clientes=("CustomerID", "nunique")).sort_values("Ingresos", ascending=False).head(25).reset_index()
    hd = c.assign(Dia=c.InvoiceDate.dt.day_name(), Hora=c.InvoiceDate.dt.hour).groupby(["Dia", "Hora"]).InvoiceNo.nunique().reset_index(name="Facturas")
    return {"ventas_mensuales": mensual, "ventas_pais": pais, "top_productos": prod, "dia_hora": hd}
