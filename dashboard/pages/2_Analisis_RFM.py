import numpy as np
import plotly.express as px
import streamlit as st
import utils as U

U.setup("Análisis RFM", "◔")
U.requiere_resultados()
U.header("Análisis RFM y variables comerciales", "Recencia, Frecuencia y Monetario: la base de la segmentación.")
N = U.notas()
cl, perf = U.clientes(), U.metrica("perfiles_segmentos.csv")
col = U.mapa_color(perf)
etiquetas = {"Recency": "Recencia (días desde la última compra)", "Frequency": "Frecuencia (nº facturas)", "Monetary": "Monetario (£ total)",
             "AvgTicket": "Ticket medio (£)", "UniqueProducts": "Productos distintos", "ReturnRate": "Tasa de devolución",
             "TenureDays": "Antigüedad (días)", "AvgItemsPerInvoice": "Unidades por factura"}

U.kpi_row([("Recencia mediana", f"{cl.Recency.median():.0f} d", f"media {cl.Recency.mean():.0f} d"), ("Frecuencia mediana", f"{cl.Frequency.median():.0f}", f"máx {cl.Frequency.max():,}"),
           ("Gasto mediano", f"£{cl.Monetary.median():,.0f}", f"máx £{cl.Monetary.max():,.0f}"), ("Ticket mediano", f"£{cl.AvgTicket.median():,.0f}", "por factura")])
st.write("")
t1, t2, t3 = st.tabs(["Distribuciones", "Relaciones", "Por segmento"])

with t1:
    v = st.selectbox("Variable", list(etiquetas), format_func=etiquetas.get)
    log_x = st.toggle("Escala logarítmica", value=v in ("Frequency", "Monetary", "AvgTicket"))
    f = px.histogram(cl, x=v, nbins=50, log_x=log_x, color_discrete_sequence=[U.C1], title=f"Distribución: {etiquetas[v]}")
    U.grafico(f, 360, False)
    U.nota(f"**{etiquetas[v]}**: mediana {cl[v].median():,.1f}, media {cl[v].mean():,.1f}, máximo {cl[v].max():,.1f}. "
           + ("Media muy por encima de la mediana = distribución muy asimétrica (pocos clientes enormes)." if cl[v].mean() > 1.5 * cl[v].median() else "Distribución relativamente equilibrada."))
    st.caption("Las variables de gasto y frecuencia son muy asimétricas (pocos clientes concentran mucho valor): por eso el modelado usa log(1+x) y estandarización.")

with t2:
    a, b = st.columns(2)
    num = ["Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts", "ReturnRate", "TenureDays"]
    corr = np.log1p(cl[num].clip(lower=0)).corr().round(2)
    with a:
        U.grafico(px.imshow(corr, text_auto=True, color_continuous_scale=U.ESCALA_DIV, zmin=-1, zmax=1, title="Correlación (variables en log)"), 420, False)
        U.nota(N["r_corr"])
    with b:
        f = px.scatter(cl, x="Frequency", y="Monetary", color="NombreSegmento", color_discrete_map=col, log_x=True, log_y=True, opacity=.6,
                       hover_data=["CustomerID", "Recency"], title="Frecuencia vs gasto (log-log)")
        f.update_traces(marker=dict(size=5)); U.grafico(f, 420)
        U.nota(N["r_scatter"])

with t3:
    v = st.selectbox("Variable a comparar", list(etiquetas), index=2, format_func=etiquetas.get, key="seg")
    f = px.box(cl, x="NombreSegmento", y=v, color="NombreSegmento", color_discrete_map=col, log_y=v in ("Frequency", "Monetary", "AvgTicket"),
               title=f"{etiquetas[v]} por segmento")
    U.grafico(f, 400, False)
    mm = cl.groupby("NombreSegmento")[v].median().sort_values(ascending=False)
    U.nota(f"Mediana más alta de **{etiquetas[v]}**: **{mm.index[0]}** ({mm.iloc[0]:,.1f}); más baja: **{mm.index[-1]}** ({mm.iloc[-1]:,.1f}). La caja marca el 50% central de cada segmento; los puntos son clientes atípicos.")
