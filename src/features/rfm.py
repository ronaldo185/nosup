"""Ingeniería de características: RFM + variables comerciales."""
import pandas as pd


def construir_rfm(c: pd.DataFrame, cancel: pd.DataFrame) -> pd.DataFrame:
    fecha_ref = c.InvoiceDate.max().normalize() + pd.Timedelta(days=1)
    g = c.groupby("CustomerID")
    r = g.agg(UltimaCompra=("InvoiceDate", "max"), PrimeraCompra=("InvoiceDate", "min"),
              Frequency=("InvoiceNo", "nunique"), Monetary=("TotalPrice", "sum"),
              UniqueProducts=("StockCode", "nunique"), TotalQuantity=("Quantity", "sum"))
    r["Recency"] = (fecha_ref - r.UltimaCompra).dt.days
    r["AvgTicket"] = r.Monetary / r.Frequency
    r["AvgItemsPerInvoice"] = r.TotalQuantity / r.Frequency
    r["TenureDays"] = (r.UltimaCompra - r.PrimeraCompra).dt.days
    r["Country"] = g.Country.agg(lambda s: s.mode().iat[0])
    nc = cancel.groupby("CustomerID").InvoiceNo.nunique()
    r["CancelledInvoices"] = nc.reindex(r.index).fillna(0).astype(int)
    r["ReturnRate"] = r.CancelledInvoices / (r.Frequency + r.CancelledInvoices)
    r = r.drop(columns=["UltimaCompra", "PrimeraCompra"]).reset_index()
    cols = ["CustomerID", "Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts", "TotalQuantity",
            "AvgItemsPerInvoice", "TenureDays", "CancelledInvoices", "ReturnRate", "Country"]
    return r[cols].round(4)
