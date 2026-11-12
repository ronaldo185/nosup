"""Perfilamiento de segmentos: estadísticos, nombre de negocio y recomendaciones."""
import numpy as np, pandas as pd

ACCIONES = {
    "Campeones": "Programa VIP, acceso anticipado a novedades y pedidos personalizados. Proteger la relación: son la base de ingresos.",
    "Clientes leales": "Venta cruzada, programa de puntos y descuentos por volumen para aumentar el ticket medio.",
    "Alto valor en riesgo": "Campaña de reactivación personalizada y contacto directo (cuenta clave): gastaron mucho pero se enfrían.",
    "En riesgo": "Recordatorios y ofertas de recompra antes de que pasen a inactivos; encuesta breve de satisfacción.",
    "Nuevos u ocasionales": "Onboarding, segunda compra incentivada y recomendaciones basadas en su primer pedido.",
    "Compradores únicos de alto ticket": "Compraron una sola vez un pedido grande y no volvieron: contacto comercial directo, oferta de recompra y revisión de su experiencia.",
    "Perdidos / inactivos": "Campaña de bajo costo de 'te extrañamos'; no invertir en retención intensiva.",
    "Clientes potenciales": "Ofertas segmentadas para aumentar frecuencia y variedad de productos.",
}


def _pct(serie, valor):
    return (serie <= valor).mean()


def nombrar(rfm, col="Segmento"):
    nombres = {}
    for s, g in rfm[rfm[col] >= 0].groupby(col):
        r = 1 - _pct(rfm.Recency, g.Recency.median())      # alto = compró recientemente
        f, m = _pct(rfm.Frequency, g.Frequency.median()), _pct(rfm.Monetary, g.Monetary.median())
        t = _pct(rfm.AvgTicket, g.AvgTicket.median())
        if f >= .75 and m >= .75 and r >= .55: n = "Campeones"
        elif f >= .6 and r >= .5: n = "Clientes leales"
        elif m >= .75: n = "Alto valor en riesgo"
        elif r <= .4 and f <= .45 and t >= .65: n = "Compradores únicos de alto ticket"
        elif r <= .3 and f <= .45: n = "Perdidos / inactivos"
        elif r <= .55 and f >= .4: n = "En riesgo"
        elif r >= .5 and f <= .55: n = "Nuevos u ocasionales"
        else: n = "Clientes potenciales"
        nombres[s] = n
    # nombres únicos: sufijo A/B/C ordenado por gasto medio
    vistos = pd.Series(nombres)
    for n, idx in vistos.groupby(vistos).groups.items():
        if len(idx) > 1:
            orden = rfm[rfm[col].isin(idx)].groupby(col).Monetary.median().sort_values(ascending=False).index
            for i, s in enumerate(orden):
                nombres[s] = f"{n} {chr(65 + i)}"
    return nombres


def perfilar(rfm, col="Segmento"):
    d = rfm[rfm[col] >= 0]
    total = d.Monetary.sum()
    p = d.groupby(col).agg(Clientes=("CustomerID", "count"), Recency=("Recency", "median"), Frequency=("Frequency", "median"),
                           Monetary=("Monetary", "median"), AvgTicket=("AvgTicket", "median"),
                           UniqueProducts=("UniqueProducts", "median"), ReturnRate=("ReturnRate", "mean"),
                           Ingresos=("Monetary", "sum")).reset_index()
    p["PctClientes"] = 100 * p.Clientes / len(rfm)
    p["PctIngresos"] = 100 * p.Ingresos / total
    nom = nombrar(rfm, col)
    p["Nombre"] = p[col].map(nom)
    p["Recomendacion"] = p.Nombre.str.replace(r" [A-Z]$", "", regex=True).map(ACCIONES)
    return p.round(2)
