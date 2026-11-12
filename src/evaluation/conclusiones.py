"""Hechos, métodos y conclusiones calculados desde los resultados reales (no texto fijo)."""
import json
import numpy as np, pandas as pd
from src import config

DIAS = {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles", "Thursday": "jueves", "Friday": "viernes",
        "Saturday": "sábado", "Sunday": "domingo"}


def _csv(n): return pd.read_csv(config.METRICS / n)


def hechos() -> dict:
    res = json.loads((config.METRICS / "resumen.json").read_text(encoding="utf-8"))
    raw = json.loads((config.METRICS / "calidad_raw.json").read_text(encoding="utf-8"))
    perf, comp, kk = _csv("perfiles_segmentos.csv"), _csv("comparacion_modelos.csv"), _csv("busqueda_kmeans_k.csv")
    mens, pais, prod, dh = _csv("eda_ventas_mensuales.csv"), _csv("eda_ventas_pais.csv"), _csv("eda_top_productos.csv"), _csv("eda_dia_hora.csv")
    ari = _csv("ari_entre_modelos.csv").set_index("Unnamed: 0")
    cl = pd.read_csv(config.PROCESSED / "clientes_segmentados.csv")
    h = {"res": res, "raw": raw, "perf": perf, "comp": comp}
    s = cl.Monetary.sort_values(ascending=False)
    h["pareto20"] = 100 * s.head(int(np.ceil(.2 * len(s)))).sum() / s.sum()
    top = perf.sort_values("PctIngresos", ascending=False).iloc[0]
    h.update(top_seg=top.Nombre, top_pct_cli=top.PctClientes, top_pct_ing=top.PctIngresos)
    h["unica_pct"] = 100 * (cl.Frequency == 1).mean()
    h["uk_pct"] = 100 * pais.loc[pais.Country == "United Kingdom", "Ingresos"].sum() / pais.Ingresos.sum()
    m = mens.loc[mens.Ingresos.idxmax()]; h["mes_pico"], h["mes_pico_ing"], h["ultimo_mes"] = m.Mes, m.Ingresos, mens.Mes.iloc[-1]
    h["hora_pico"] = int(dh.groupby("Hora").Facturas.sum().idxmax())
    d = dh.groupby("Dia").Facturas.sum(); h["dia_pico"] = DIAS[d.idxmax()]
    h["dias_sin_ventas"] = [DIAS[x] for x in DIAS if x not in d.index]
    h["prod_top"] = prod.Description.iloc[0].title()
    h["sin_cliente_pct"] = 100 * raw["nulos"]["CustomerID"] / raw["filas"]
    h["devol_media"] = 100 * cl.ReturnRate.mean()
    h["media_mediana"] = cl.Monetary.mean() / cl.Monetary.median()
    k = kk.set_index("k"); h["sil_k2"], h["k_final"] = float(k.silhouette[2]), res["n_segmentos"]
    a = ari.values; h["ari_medio"] = float(a[~np.eye(len(a), dtype=bool)].mean())
    c = np.log1p(cl[config.FEATURES]).corr(); iu = np.triu_indices(len(c), 1)
    j = np.argmax(np.abs(c.values[iu])); h["corr_par"] = (c.index[iu[0][j]], c.columns[iu[1][j]], float(c.values[iu][j]))
    e = comp.dropna(subset=["silhouette"])
    h["mejor_sil"], h["mejor_db"] = e.loc[e.silhouette.idxmax(), "modelo"], e.loc[e.davies_bouldin.idxmin(), "modelo"]
    h["mejor_ch"], h["mejor_est"] = e.loc[e.calinski_harabasz.idxmax(), "modelo"], e.loc[e.estabilidad_ari.idxmax(), "modelo"]
    return h


def _est(h, m):
    c = h["comp"].set_index("modelo")
    return f"{c.loc[m].estabilidad_ari:.2f}" if m in c.index else "n/d"


def notas(h) -> dict:
    r, p = h["res"], h["perf"]
    var = r.get("pca_var", [0, 0])
    return {
        "app_barras": f"Barra clara = % de clientes; barra de color = % de ingresos. La brecha entre ambas mide la concentración del valor: "
                      f"**{h['top_seg']}** pasa de {h['top_pct_cli']:.0f}% de los clientes a {h['top_pct_ing']:.0f}% de los ingresos.",
        "app_pca": f"Cada punto es un cliente proyectado en 2 dimensiones (PC1+PC2 explican {100 * sum(var):.0f}% de la variabilidad). Los colores se tocan sin "
                   "separarse del todo: los comportamientos forman un **continuo**, no islas, lo que explica un silhouette moderado.",
        "d_waterfall": f"El mayor filtro es quitar las filas sin CustomerID ({h['sin_cliente_pct']:.0f}% del total): sin identificar al cliente no se puede "
                       "segmentar. El resto de pasos elimina muy pocas filas.",
        "d_nulos": "Solo Description y CustomerID tienen nulos. Los de CustomerID son compras sin cliente registrado (probablemente ventas sin cuenta).",
        "d_mensual": f"El mes de mayores ingresos es **{h['mes_pico']}** (£{h['mes_pico_ing'] / 1e3:,.0f}K): hay estacionalidad fuerte hacia el final del año "
                     f"(probablemente por las compras de fin de año). {h['ultimo_mes']} está incompleto (el dataset termina el 9-dic), por eso cae.",
        "d_horas": f"La actividad se concentra alrededor de las {h['hora_pico']}:00 h y los días hábiles; el día con más facturas es el {h['dia_pico']}"
                   + (f" y no hay ventas el {', '.join(h['dias_sin_ventas'])}." if h["dias_sin_ventas"] else "."),
        "d_pais": f"El Reino Unido aporta ~{h['uk_pct']:.0f}% de los ingresos. Los demás países son pocos clientes con pedidos grandes, por lo que el país "
                  "no se usó para agrupar.",
        "d_prod": f"Los ingresos están repartidos entre muchos productos (el primero es «{h['prod_top']}»): no depende de un único artículo.",
        "r_corr": f"Pares más correlacionados: **{h['corr_par'][0]}–{h['corr_par'][1]}** (r={h['corr_par'][2]:.2f}). Clientes que compran más veces compran más "
                  "variedad y gastan más: por eso Frecuencia, Monetario y Productos están relacionados, y la Recencia aporta información distinta.",
        "r_scatter": f"Relación casi lineal en escala log-log: más facturas → más gasto. Los clientes de una sola factura ({h['unica_pct']:.0f}% de la base) "
                     "se ven en la columna izquierda, con gastos muy diversos (ticket alto vs. bajo).",
        "m_barras": f"Mejor silhouette: **{h['mejor_sil']}**; menor Davies-Bouldin: **{h['mejor_db']}**; mayor Calinski-Harabasz: **{h['mejor_ch']}**; "
                    f"más estable: **{h['mejor_est']}**. Ningún modelo gana en todo: por eso se usa un ranking compuesto.",
        "m_codo": "La inercia baja de forma gradual al subir k, sin un codo claro: no existe un k «obvio». Es otra señal de continuo.",
        "m_sil": f"El silhouette es máximo con k=2 ({h['sil_k2']:.2f}: clientes activos vs. inactivos) y decrece al subir k. Se eligió k={h['k_final']} "
                 f"({r['silhouette_final']:.2f}) porque 2-3 grupos son demasiado gruesos para actuar comercialmente.",
        "m_gmm": "BIC/AIC más bajos = mejor ajuste probabilístico. Si siguen cayendo al subir k, la mezcla usa componentes extra para modelar la "
                 "asimetría, no grupos de negocio distintos.",
        "m_jer": f"Silhouette del método jerárquico por k. Su estabilidad en submuestras es {_est(h, 'Jerárquico (Ward)')} frente a {_est(h, 'K-Means')} de K-Means: cambia mucho al variar la muestra.",
        "m_dbscan": "Zonas brillantes = más % de ruido. Un eps pequeño o min_samples alto deja a muchos clientes sin grupo; un eps grande fusiona todo en 1–2 grupos.",
        "m_ari": f"Acuerdo medio entre algoritmos: ARI = {h['ari_medio']:.2f} (0 = azar, 1 = idénticos). Cada método traza fronteras distintas porque los "
                 "datos no tienen grupos bien separados.",
        "s_radar": "Cada eje está normalizado entre segmentos (más lejos del centro = más alto; en «actividad reciente», más lejos = compró hace menos). "
                   "La forma del polígono resume el perfil: un polígono grande = cliente valioso en todo.",
        "s_pie": f"El reparto de ingresos está muy desbalanceado: **{h['top_seg']}** concentra {h['top_pct_ing']:.0f}%. "
                 f"En general, el 20% de clientes que más gastan genera ~{h['pareto20']:.0f}% de los ingresos (principio de Pareto).",
    }


def metodos(h) -> dict:
    c = h["comp"].set_index("modelo")

    def res(m):
        if m not in c.index: return "No se obtuvo una configuración válida."
        r = c.loc[m]
        sil = "n/d" if pd.isna(r.silhouette) else f"{r.silhouette:.3f}"
        return f"{int(r.n_clusters)} grupos · silhouette {sil} · ruido {r.ruido_pct:.1f}% · estabilidad {r.estabilidad_ari:.2f}"
    A = [
        ("K-Means", "Divide a los clientes en k grupos esféricos alrededor de centroides, minimizando la distancia interna.",
         "Rápido, fácil de interpretar y de explicar al negocio; asigna a todos los clientes.", "Supone grupos de forma esférica y tamaño similar; sensible a atípicos.", "k = 2…10"),
        ("Jerárquico (Ward)", "Agrupa de abajo hacia arriba fusionando los grupos que menos aumentan la varianza interna.",
         "No necesita fijar k de antemano (se puede cortar el árbol donde convenga) y muestra relaciones entre grupos.", "Costoso para bases enormes y muy sensible a pequeños cambios en los datos.", "k = 2…10"),
        ("GMM", "Modela los datos como una mezcla de distribuciones gaussianas; cada cliente tiene probabilidad de pertenecer a cada grupo.",
         "Grupos elípticos y pertenencia «suave» (probabilidades).", "Supone normalidad; con datos asimétricos tiende a crear grupos solapados.", "k = 2…10 (BIC)"),
        ("DBSCAN", "Agrupa zonas densas de clientes y marca como ruido a los que quedan aislados.",
         "Detecta formas arbitrarias y atípicos sin fijar k.", "Un solo eps para toda la densidad; deja clientes sin segmento.", "eps 0.3–1.3 × min_samples {5,10,15,20}"),
        ("HDBSCAN", "Versión jerárquica de DBSCAN que encuentra clusters de densidades distintas.",
         "Robusto a densidades variables y con pocos parámetros.", "Aquí descarta un porcentaje alto de clientes como ruido.", "min_cluster_size {20…150} × min_samples {5,10,20}"),
    ]
    return {"algoritmos": [dict(nombre=a[0], que=a[1], ventaja=a[2], limite=a[3], params=a[4], resultado=res(a[0])) for a in A]}


def mejor_modelo(h) -> dict:
    r, c = h["res"], h["comp"]
    el = c[c.elegible].sort_values("ranking_compuesto")
    return {"modelo": r["modelo_final"], "params": r["modelo_final_params"],
            "veredicto": (f"El mejor modelo para este proyecto es **{r['modelo_final']}** {r['modelo_final_params']}: obtiene el mejor ranking compuesto "
                          f"entre los modelos elegibles (silhouette {r['silhouette_final']:.3f}, Davies-Bouldin {r['davies_bouldin_final']:.2f}, "
                          f"Calinski-Harabasz {r['calinski_final']:,.0f}, estabilidad {r['estabilidad_final']:.2f}, sin ruido), "
                          "y además produce segmentos que el negocio puede entender y accionar."),
            "ranking": el[["modelo", "ranking_compuesto", "silhouette", "davies_bouldin", "calinski_harabasz", "estabilidad_ari"]],
            "no_elegibles": c[~c.elegible].modelo.tolist(),
            "conviene": [
                ("Segmentar clientes para campañas de marketing", "K-Means", "Asigna a todos los clientes, grupos claros y estables."),
                ("Detectar clientes atípicos o mayoristas", "HDBSCAN / DBSCAN", "Marcan como ruido a los clientes que no encajan en ningún grupo."),
                ("Estimar la probabilidad de pertenecer a cada segmento", "GMM", "Entrega probabilidades por segmento, útil para clientes en la frontera."),
                ("Explorar cómo se relacionan los grupos entre sí", "Jerárquico (Ward)", "El árbol muestra qué segmentos se fusionan primero."),
            ]}


def hallazgos(h) -> list:
    r, p = h["res"], h["perf"].sort_values("Segmento")
    seg = "; ".join(f"**{x.Nombre}** ({x.PctClientes:.0f}% clientes, {x.PctIngresos:.0f}% ingresos)" for x in p.itertuples())
    return [
        ("Datos", f"Se partió de {r['filas_raw']:,} registros y quedaron {r['filas_limpias']:,} compras válidas de {r['clientes']:,} clientes. "
                  f"{h['sin_cliente_pct']:.0f}% de las filas no tenía CustomerID y se descartó."),
        ("Concentración del valor", f"El 20% de los clientes que más gastan genera ~{h['pareto20']:.0f}% de los ingresos. El gasto medio es {h['media_mediana']:.1f} veces la "
                                    "mediana: pocos clientes muy grandes elevan el promedio."),
        ("Recompra", f"{h['unica_pct']:.0f}% de los clientes compró una sola vez en el periodo: la fidelización es la mayor oportunidad."),
        ("Estacionalidad", f"Las ventas suben hacia el final del año; el pico es {h['mes_pico']}."),
        ("Devoluciones", f"En promedio, {h['devol_media']:.1f}% de las facturas de un cliente son cancelaciones."),
        ("Segmentos descubiertos", seg + "."),
        ("Calidad de la estructura", f"El silhouette ({r['silhouette_final']:.2f}) es moderado y el acuerdo entre algoritmos es bajo (ARI {h['ari_medio']:.2f}): "
                                     "los clientes forman un continuo, no grupos aislados. Los segmentos son útiles como convención de negocio, no como categorías «naturales»."),
    ]


def conclusiones(h) -> dict:
    r, p = h["res"], h["perf"].sort_values("Segmento")
    return {"conclusiones": [
        f"Es posible segmentar a los clientes sin etiquetas previas: se identificaron **{r['n_segmentos']} segmentos** con {r['modelo_final']}.",
        f"El valor está muy concentrado: **{h['top_seg']}** ({h['top_pct_cli']:.0f}% de clientes) genera {h['top_pct_ing']:.0f}% de los ingresos.",
        "No hay un único algoritmo «mejor» en todas las métricas; la elección depende del objetivo. Para marketing, K-Means ofrece el mejor equilibrio.",
        f"Los datos forman un continuo (silhouette {r['silhouette_final']:.2f}); por eso se priorizó la interpretabilidad y la estabilidad sobre maximizar una métrica.",
        "La combinación de RFM + ticket medio + variedad de productos permite distinguir perfiles que RFM por sí solo no separaría (p. ej., compradores únicos de ticket alto).",
    ], "acciones": [(x.Nombre, x.Recomendacion) for x in p.itertuples()],
        "limitaciones": [
            "Un solo minorista del Reino Unido y solo 12 meses: no se pueden generalizar los resultados ni medir ciclos anuales completos.",
            "Gran presencia de mayoristas: sus compras elevan el gasto y condicionan la separación entre grupos.",
            "No hay etiquetas reales para validar externamente; solo métricas internas y estabilidad.",
            "Los segmentos describen comportamiento pasado; deben recalcularse periódicamente (el dashboard permite re-ejecutar el pipeline)."],
        "futuro": ["Añadir categoría de producto y estacionalidad como variables.", "Predecir abandono (churn) y valor futuro (CLV) usando los segmentos.",
                   "Probar embeddings o reducción de dimensionalidad (UMAP) antes de agrupar.", "Validar con pruebas A/B de campañas por segmento."]}
