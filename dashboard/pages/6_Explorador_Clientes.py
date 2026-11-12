import plotly.express as px
import streamlit as st
import utils as U

U.setup("Explorador de clientes", "⌕")
U.requiere_resultados()
U.header("Explorador de clientes", "Filtra, busca y exporta clientes con su segmento asignado.")
cl, perf = U.clientes(), U.metrica("perfiles_segmentos.csv")
col = U.mapa_color(perf)

with st.sidebar:
    st.markdown("**Filtros**")
    segs = st.multiselect("Segmento", sorted(cl.NombreSegmento.unique()), default=sorted(cl.NombreSegmento.unique()))
    paises = st.multiselect("País", sorted(cl.Country.unique()))
    rec = st.slider("Recencia (días)", 0, int(cl.Recency.max()), (0, int(cl.Recency.max())))
    mon = st.slider("Gasto mínimo (£)", 0, int(cl.Monetary.quantile(.99)), 0)
    freq = st.slider("Frecuencia mínima", 1, int(cl.Frequency.quantile(.99)), 1)
    idb = st.text_input("Buscar CustomerID")

f = cl[cl.NombreSegmento.isin(segs) & cl.Recency.between(*rec) & (cl.Monetary >= mon) & (cl.Frequency >= freq)]
if paises: f = f[f.Country.isin(paises)]
if idb.strip().isdigit(): f = f[f.CustomerID == int(idb)]

U.kpi_row([("Clientes", f"{len(f):,}", f"{100 * len(f) / len(cl):.1f}% del total"), ("Ingresos", f"£{f.Monetary.sum():,.0f}", f"{100 * f.Monetary.sum() / cl.Monetary.sum():.1f}% del total"),
           ("Recencia mediana", f"{f.Recency.median():.0f} d" if len(f) else "–", ""), ("Gasto mediano", f"£{f.Monetary.median():,.0f}" if len(f) else "–", "")])
st.write("")
if f.empty:
    st.info("Sin resultados con estos filtros."); st.stop()
a, b = st.columns(2)
ejes = ["Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts"]
with a: x = st.selectbox("Eje X", ejes, 1)
with b: y = st.selectbox("Eje Y", ejes, 2)
fig = px.scatter(f, x=x, y=y, color="NombreSegmento", color_discrete_map=col, opacity=.65, log_x=x != "Recency", log_y=y != "Recency",
                 hover_data=["CustomerID", "Country"]); fig.update_traces(marker=dict(size=6))
U.grafico(fig, 420)
cols = ["CustomerID", "NombreSegmento", "Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts", "ReturnRate", "Country"]
st.dataframe(f[cols].sort_values("Monetary", ascending=False), use_container_width=True, hide_index=True, height=360)
st.download_button("⬇ Exportar selección (CSV)", f[cols].to_csv(index=False).encode("utf-8"), "clientes_filtrados.csv", "text/csv",
                   on_click=lambda: U.log.info(f"Exportación CSV: {len(f)} clientes filtrados"))
