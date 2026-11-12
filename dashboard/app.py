"""Inicio: resumen ejecutivo.  Ejecutar:  streamlit run dashboard/app.py"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils as U

U.setup("Resumen", "◼")
U.requiere_resultados()
N = U.notas()
H = U.hechos()

res, perf, cl = U.metrica("resumen.json"), U.metrica("perfiles_segmentos.csv"), U.clientes()
colores = U.mapa_color(perf)

U.header("Segmentación inteligente de clientes",
         f"Periodo {res['fecha_min'][:10]} → {res['fecha_max'][:10]} · {res['modelo_final']} · variables: {', '.join(res['features'])}")
U.kpi_row([("Clientes", f"{res['clientes']:,}", "con compras válidas"), ("Ingresos", f"£{res['ingresos']/1e6:,.2f}M", f"{res['facturas']:,} facturas"),
           ("Segmentos", res["n_segmentos"], res["modelo_final"]), ("Silhouette", f"{res['silhouette_final']:.3f}", f"Davies-Bouldin {res['davies_bouldin_final']:.2f}"),
           ("Estabilidad", f"{res['estabilidad_final']:.2f}", "ARI en submuestras")])
st.write("")

top = perf.sort_values("PctIngresos", ascending=False).iloc[0]
st.markdown(f"<div class='banner'><b>Hallazgo principal:</b> el segmento <b>{top.Nombre}</b> agrupa solo el "
            f"<b>{top.PctClientes:.0f}%</b> de los clientes pero genera el <b>{top.PctIngresos:.0f}%</b> de los ingresos. "
            f"Retenerlo es la prioridad comercial.</div>", unsafe_allow_html=True)

st.markdown("### En pocas palabras")
d1, d2, d3 = st.columns(3)
with d1: U.card("Qué hicimos", "Limpiamos las transacciones, resumimos a cada cliente (RFM + ticket + variedad) y probamos 5 algoritmos de agrupamiento sin etiquetas previas.")
with d2: U.card("Qué encontramos", f"{res['n_segmentos']} segmentos. El 20% de clientes que más gastan aporta ~{H['pareto20']:.0f}% de los ingresos y {H['unica_pct']:.0f}% compró una sola vez.")
with d3: U.card("Mejor modelo", f"{res['modelo_final']} {res['modelo_final_params']}: mejor equilibrio entre separación, estabilidad e interpretabilidad. Ver «Métodos y conclusiones».")

c1, c2 = st.columns([1, 1.25])
with c1:
    f = go.Figure()
    f.add_bar(x=perf.Nombre, y=perf.PctClientes, name="% clientes", marker_color=U.SUAVE)
    f.add_bar(x=perf.Nombre, y=perf.PctIngresos, name="% ingresos", marker_color=U.C1)
    f.update_layout(barmode="group", title="Peso de cada segmento")
    U.grafico(f, 380)
    U.nota(N["app_barras"])
with c2:
    fig = px.scatter(cl, x="PC1", y="PC2", color="NombreSegmento", color_discrete_map=colores, opacity=.65,
                     hover_data=["CustomerID", "Recency", "Frequency", "Monetary"], title="Mapa de clientes (PCA)")
    fig.update_traces(marker=dict(size=5))
    U.grafico(fig, 380)
    U.nota(N["app_pca"])

st.markdown("### Segmentos y acciones recomendadas")
cols = st.columns(2)
for i, p in enumerate(perf.sort_values("Segmento").itertuples()):
    with cols[i % 2]:
        U.card(f"{p.Nombre}", f"{p.Recomendacion}",
               pills=(f"{int(p.Clientes):,} clientes", f"{p.PctIngresos:.0f}% ingresos", f"recencia {p.Recency:.0f} d", f"£{p.Monetary:,.0f} mediana"))

st.markdown("### Reporte")
pdf_path = U.config.RESULTS / "reporte_ejecutivo.pdf"
if pdf_path.exists():
    st.download_button("⬇ Descargar reporte ejecutivo (PDF)", pdf_path.read_bytes(), "reporte_ejecutivo.pdf", "application/pdf",
                       on_click=lambda: U.log.info("Descarga: reporte ejecutivo PDF"))
