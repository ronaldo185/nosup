"""Carga de datos. Nunca modifica el archivo original."""
import pandas as pd
from src import config


def localizar_raw():
    for patron in ("Online Retail.xlsx", "Online_Retail.xlsx", "*.xlsx", "*.csv"):
        enc = [p for p in config.RAW.glob(patron) if "diccionario" not in p.name.lower()]
        if enc:
            return enc[0]
    raise FileNotFoundError(f"Coloca el dataset UCI Online Retail en {config.RAW}")


def cargar_raw() -> pd.DataFrame:
    ruta = localizar_raw()
    df = pd.read_excel(ruta) if ruta.suffix == ".xlsx" else pd.read_csv(ruta, encoding="latin-1", parse_dates=["InvoiceDate"])
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    return df
