import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils as U
from src.reporting import pdf

U.setup("Segmentos", "◍")
U.requiere_resultados()
U.header("Perfiles de segmentos", "Quién es cada grupo, cuánto aporta y qué hacer con él.")
N = U.notas()
perf, cl = U.metrica("perfiles_segmentos.csv").sort_values("Segmento"), U.clientes()
col = U.mapa_color(perf)

# Radar comparativo
cols = ["Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts"]
z = (perf[cols] - perf[cols].min()) / (perf[cols].max() - perf[cols].min() + 1e-9); z["Recency"] = 1 - z["Recency"]
nombres = ["Actividad reciente", "Frecuencia", "Gasto", "Ticket medio", "Variedad"]
f = go.Figure()
for i, p in enumerate(perf.itertuples()):
    f.add_trace(go.Scatterpolar(r=list(z.iloc[i]) + [z.iloc[i, 0]], theta=nombres + nombres[:1], name=p.Nombre, fill="toself", opacity=.55,
                                line=dict(color=col[p.Nombre])))
f.update_layout(title="Comparación de segmentos (valores relativos)", polar=dict(radialaxis=dict(visible=False, range=[0, 1])))
a, b = st.columns([1, 1])
with a: U.grafico(f, 420); U.nota(N["s_radar"])
with b:
    d = px.pie(perf, names="Nombre", values="Ingresos", hole=.62, color="Nombre", color_discrete_map=col, title="Reparto de ingresos")
    U.grafico(d, 420)
    U.nota(N["s_pie"])

st.markdown("### Detalle por segmento")
sel = st.selectbox("Segmento", perf.Segmento, format_func=lambda s: f"#{s} · {perf[perf.Segmento == s].Nombre.iloc[0]}")
p = perf[perf.Segmento == sel].iloc[0]; g = cl[cl.Segmento == sel]
U.kpi_row([("Clientes", f"{int(p.Clientes):,}", f"{p.PctClientes:.1f}% de la base"), ("Ingresos", f"£{p.Ingresos/1e3:,.0f}K", f"{p.PctIngresos:.1f}% del total"),
           ("Recencia", f"{p.Recency:.0f} d", "mediana"), ("Frecuencia", f"{p.Frequency:.0f}", "facturas, mediana"), ("Gasto", f"£{p.Monetary:,.0f}", "mediana por cliente")])
st.write("")
U.card(f"Acción recomendada · {p.Nombre}", p.Recomendacion, pills=(f"ticket £{p.AvgTicket:,.0f}", f"{p.UniqueProducts:.0f} productos", f"devoluciones {p.ReturnRate:.1%}"))
a, b = st.columns(2)
pais = g.Country.value_counts().head(8).reset_index(); pais.columns = ["País", "Clientes"]
f = px.bar(pais.iloc[::-1], x="Clientes", y="País", orientation="h", title="Principales países"); f.update_traces(marker_color=col[p.Nombre])
with a: U.grafico(f, 330, False)
f = px.histogram(g, x="Monetary", nbins=30, log_x=True, title="Distribución del gasto (log)"); f.update_traces(marker_color=col[p.Nombre])
with b: U.grafico(f, 330, False)
st.markdown("**Mejores clientes del segmento**")
st.dataframe(g.sort_values("Monetary", ascending=False).head(10)[["CustomerID", "Recency", "Frequency", "Monetary", "AvgTicket", "Country"]],
             use_container_width=True, hide_index=True)
st.download_button("⬇ Ficha del segmento (PDF)", pdf.ficha_segmento(int(sel)), f"ficha_segmento_{sel}.pdf", "application/pdf",
                   on_click=lambda: U.log.info(f"Descarga: ficha PDF del segmento {sel}"))
