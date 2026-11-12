import streamlit as st
import utils as U
from src.evaluation import conclusiones as C

U.setup("Métodos y conclusiones", "✓")
U.requiere_resultados()
U.header("Métodos y conclusiones", "Qué hicimos, qué encontramos y qué modelo conviene. Los textos se recalculan con cada ejecución.")
H = U.hechos(); R = H["res"]
MB, HA, CO, ME = C.mejor_modelo(H), C.hallazgos(H), C.conclusiones(H), C.metodos(H)

t1, t2, t3, t4, t5 = st.tabs(["Métodos", "Hallazgos", "Mejor modelo", "Conclusiones", "Limitaciones y futuro"])

with t1:
    st.markdown("### Flujo de trabajo")
    pasos = [("1 · Datos", "UCI Online Retail (541.909 líneas, dic-2010 a dic-2011)."),
             ("2 · Procesamiento", "Duplicados, clientes nulos, códigos que no son producto, cancelaciones y valores no válidos."),
             ("3 · Características", "RFM + ticket medio + variedad de productos → log(1+x) → estandarización."),
             ("4 · Machine Learning", "K-Means, Jerárquico, GMM, DBSCAN y HDBSCAN."),
             ("5 · Evaluación", "Silhouette, Davies-Bouldin, Calinski-Harabasz, estabilidad (ARI) y acuerdo entre modelos."),
             ("6 · Interpretación", "Perfiles de negocio con nombre y acción recomendada; clasificador para clientes nuevos.")]
    cols = st.columns(3)
    for i, (t, d) in enumerate(pasos):
        with cols[i % 3]: U.card(t, d)
    st.markdown("### Algoritmos comparados")
    for a in ME["algoritmos"]:
        U.card(a["nombre"], f"<b>Qué hace:</b> {a['que']}<br><b>Ventaja:</b> {a['ventaja']}<br><b>Limitación:</b> {a['limite']}<br>"
                            f"<b>Resultado aquí:</b> {a['resultado']}", pills=(a["params"],))
    st.markdown("### Cómo se midió la calidad")
    st.markdown("""
- **Silhouette** (−1 a 1, mayor es mejor): separación entre grupos.
- **Davies-Bouldin** (menor es mejor): parecido entre cada grupo y su vecino más cercano.
- **Calinski-Harabasz** (mayor es mejor): dispersión entre grupos vs. dentro de grupos.
- **Estabilidad (ARI)**: cuánto se repite la partición al re-entrenar con submuestras del 80%.
- **Ruido %**: clientes que DBSCAN/HDBSCAN no asignan a ningún grupo.
- **Selección final**: ranking compuesto entre modelos *elegibles* (4–8 grupos y ≤10% de ruido).""")

with t2:
    st.markdown("### Qué encontramos")
    for t, d in HA:
        U.card(t, d.replace("**", ""))

with t3:
    st.markdown(f"<div class='banner'>{MB['veredicto'].replace('**', '<b>', 1).replace('**', '</b>', 1)}</div>", unsafe_allow_html=True)
    st.markdown("### Ranking entre modelos elegibles")
    r = MB["ranking"].rename(columns={"modelo": "Modelo", "ranking_compuesto": "Ranking (↓ mejor)", "silhouette": "Silhouette ↑",
                                      "davies_bouldin": "Davies-Bouldin ↓", "calinski_harabasz": "Calinski-H. ↑", "estabilidad_ari": "Estabilidad ↑"}).round(3)
    st.dataframe(r, use_container_width=True, hide_index=True)
    if MB["no_elegibles"]:
        U.nota(f"Descartados por no cumplir el criterio de elegibilidad (grupos fuera de 4–8 o ruido > 10%): **{', '.join(MB['no_elegibles'])}**. "
               "Pueden tener buenas métricas internas, pero dejan clientes sin segmento o producen pocos grupos para actuar.")
    st.markdown("### ¿Cuál conviene según el objetivo?")
    for obj, mod, por in MB["conviene"]:
        U.card(obj, por, pills=(f"→ {mod}",))

with t4:
    st.markdown("### Conclusiones")
    for i, c in enumerate(CO["conclusiones"], 1):
        U.card(f"{i}", c.replace("**", ""))
    st.markdown("### Acción recomendada por segmento")
    for n, a in CO["acciones"]:
        U.card(n, a)

with t5:
    a, b = st.columns(2)
    with a:
        st.markdown("### Limitaciones")
        for x in CO["limitaciones"]: U.card("•", x)
    with b:
        st.markdown("### Trabajo futuro")
        for x in CO["futuro"]: U.card("•", x)
