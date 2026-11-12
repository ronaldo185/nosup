"""Limpieza del dataset con trazabilidad de cada paso."""
import pandas as pd
from src import config


def limpiar(df: pd.DataFrame):
    """Devuelve (compras_limpias, cancelaciones, bitacora_pasos)."""
    pasos, actual = [], df.copy()

    def registrar(nombre, nuevo, motivo):
        pasos.append({"paso": nombre, "filas_antes": len(actual), "filas_despues": len(nuevo),
                      "eliminadas": len(actual) - len(nuevo), "motivo": motivo})
        return nuevo

    actual = registrar("Duplicados exactos", actual.drop_duplicates(), "Registros repetidos inflan frecuencia y gasto")
    actual = registrar("Sin CustomerID", actual.dropna(subset=["CustomerID"]), "No se puede segmentar sin identificar al cliente")
    actual = registrar("Códigos no-producto", actual[~actual.StockCode.isin(config.NO_PRODUCTO)],
                       "POST, DOT, BANK CHARGES, etc. no son compras de producto")
    es_cancel = actual.InvoiceNo.str.upper().str.startswith("C")
    cancel = actual[es_cancel].copy()
    actual = registrar("Cancelaciones (facturas 'C')", actual[~es_cancel], "Se separan: alimentan la tasa de devolución")
    actual = registrar("Cantidad <= 0", actual[actual.Quantity > 0], "Ajustes/pérdidas, no ventas")
    actual = registrar("Precio unitario <= 0", actual[actual.UnitPrice > 0], "Ajustes contables / regalos sin valor")

    actual = actual.copy()
    actual["CustomerID"] = actual.CustomerID.astype(int)
    actual["Description"] = actual.Description.fillna("SIN DESCRIPCION").str.strip()
    actual["TotalPrice"] = actual.Quantity * actual.UnitPrice
    cancel["CustomerID"] = cancel.CustomerID.astype(int)
    return actual.reset_index(drop=True), cancel.reset_index(drop=True), pd.DataFrame(pasos)
