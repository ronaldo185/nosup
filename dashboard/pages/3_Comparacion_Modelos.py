import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils as U

U.setup("Comparación de modelos", "⇄")
U.requiere_resultados()
U.header("Comparación de algoritmos", "K-Means · Jerárquico (Ward) · GMM · DBSCAN · HDBSCAN")
N = U.notas()
res, comp = U.metrica("resumen.json"), U.metrica("comparacion_modelos.csv")
st.markdown(f"<div class='banner'><b>Modelo seleccionado: {res['modelo_final']}</b> {res['modelo_final_params']}. "
            "Criterio: ranking compuesto (silhouette, Davies-Bouldin, Calinski-Harabasz y estabilidad) entre modelos <i>elegibles</i> "
            "(4-8 grupos y ≤10% de ruido), para obtener segmentos accionables.</div>", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["Resumen", "Búsqueda de parámetros", "Acuerdo entre modelos", "Cómo leer las métricas"])
with t1:
    v = comp.rename(columns={"modelo": "Modelo", "parametros": "Parámetros", "n_clusters": "Grupos", "ruido_pct": "Ruido %", "silhouette": "Silhouette ↑",
                             "davies_bouldin": "Davies-Bouldin ↓", "calinski_harabasz": "Calinski-H. ↑", "estabilidad_ari": "Estabilidad ↑",
                             "elegible": "Elegible", "ranking_compuesto": "Ranking ↓"}).round(3)
    st.dataframe(v, use_container_width=True, hide_index=True)
    cols = st.columns(4)
    for c, (m, t, mejor) in zip(cols, [("silhouette", "Silhouette", "max"), ("davies_bouldin", "Davies-Bouldin", "min"),
                                       ("calinski_harabasz", "Calinski-Harabasz", "max"), ("estabilidad_ari", "Estabilidad (ARI)", "max")]):
        f = px.bar(comp, x="modelo", y=m, color="modelo", title=t); f.update_xaxes(title="", tickangle=-35); f.update_yaxes(title="")
        with c: U.grafico(f, 300, False)
    U.nota(N["m_barras"])
    st.caption("HDBSCAN suele obtener silhouette alto porque descarta como ruido a los clientes atípicos (ver columna Ruido %): no es comparable sin ese contexto.")

with t2:
    k = U.metrica("busqueda_kmeans_k.csv")
    a, b = st.columns(2)
    f = go.Figure(); f.add_scatter(x=k.k, y=k.inercia, mode="lines+markers", line=dict(color=U.C1)); f.update_layout(title="K-Means: método del codo (inercia)")
    with a: U.grafico(f, 320, False); U.nota(N["m_codo"])
    f = go.Figure(); f.add_scatter(x=k.k, y=k.silhouette, mode="lines+markers", name="Silhouette", line=dict(color=U.C3))
    f.add_scatter(x=k.k, y=k.davies_bouldin, mode="lines+markers", name="Davies-Bouldin", line=dict(color=U.C5)); f.update_layout(title="K-Means: silhouette y Davies-Bouldin")
    with b: U.grafico(f, 320); U.nota(N["m_sil"])
    g = U.metrica("busqueda_gmm_k.csv"); a, b = st.columns(2)
    f = go.Figure(); f.add_scatter(x=g.k, y=g.bic, name="BIC", mode="lines+markers"); f.add_scatter(x=g.k, y=g.aic, name="AIC", mode="lines+markers")
    f.update_layout(title="GMM: BIC / AIC")
    with a: U.grafico(f, 320); U.nota(N["m_gmm"])
    j = U.metrica("busqueda_jerarquico_k.csv")
    f = px.line(j, x="k", y="silhouette", markers=True, title="Jerárquico (Ward): silhouette"); f.update_traces(line_color=U.C6)
    with b: U.grafico(f, 320, False); U.nota(N["m_jer"])
    d = U.metrica("busqueda_dbscan_grid.csv")
    f = px.density_heatmap(d, x="eps", y="min_samples", z="ruido_pct", histfunc="avg", color_continuous_scale=U.ESCALA, title="DBSCAN: % de ruido por eps y min_samples")
    a, b = st.columns(2)
    with a: U.grafico(f, 320, False); U.nota(N["m_dbscan"])
    h = U.metrica("busqueda_hdbscan_grid.csv")
    with b: st.dataframe(h.round(3), use_container_width=True, hide_index=True, height=320)
    st.caption("Tabla: rejilla de HDBSCAN (min_cluster_size × min_samples).")

with t3:
    ari = U.metrica("ari_entre_modelos.csv").set_index("Unnamed: 0")
    f = px.imshow(ari, text_auto=".2f", color_continuous_scale=U.ESCALA, zmin=0, zmax=1, title="Índice de Rand ajustado entre particiones")
    U.grafico(f, 440, False)
    U.nota(N["m_ari"])
    st.caption("ARI = 1 significa particiones idénticas; ≈0, acuerdo igual al azar. Valores bajos entre modelos indican que los datos forman un continuo sin fronteras nítidas.")

with t4:
    st.markdown("""
- **Silhouette** (−1 a 1): qué tan separado está cada cliente de otros grupos. >0.5 fuerte, 0.25–0.5 razonable, <0.25 débil.
- **Davies-Bouldin** (≥0, menor es mejor): similitud media entre cada grupo y su vecino más parecido.
- **Calinski-Harabasz** (mayor es mejor): razón entre dispersión entre grupos y dentro de grupos.
- **Estabilidad (ARI)**: se ajusta el modelo en dos submuestras del 80% y se compara la partición en los clientes comunes; cerca de 1 = reproducible.
- **Ruido %**: clientes que DBSCAN/HDBSCAN no asignan a ningún grupo; se excluyen de las métricas internas.
""")
