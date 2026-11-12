"""Ejecuta los 5 algoritmos, los evalúa y selecciona el mejor con criterios explícitos."""
import numpy as np, pandas as pd
from sklearn.metrics import adjusted_rand_score
from src import config
from src.models import kmeans, jerarquico, gmm, dbscan, hdbscan_model
from src.evaluation.metricas import evaluar, estabilidad
from src.utils.bitacora import get_logger

log = get_logger("modelos")


def _mejor_k(tabla, col, maximizar=True):
    t = tabla[(tabla.k >= config.K_MIN_NEGOCIO) & (tabla.k <= config.K_MAX_NEGOCIO)]
    return int(t.loc[t[col].idxmax() if maximizar else t[col].idxmin(), "k"])


def _mejor_density(grid, cols):
    ok = grid[(grid.n_clusters >= config.K_MIN_NEGOCIO) & (grid.n_clusters <= 10) & (grid.ruido_pct <= 15) & grid.silhouette.notna()]
    if ok.empty:   # relaja restricciones
        ok = grid[(grid.n_clusters >= 2) & grid.silhouette.notna()]
    if ok.empty:
        return None
    return ok.loc[ok.silhouette.idxmax(), cols].to_dict()


def comparar(X, k_forzado=None):
    R, tablas = {}, {}

    log.info("K-Means: búsqueda de k (2-10)")
    tablas["kmeans_k"] = kmeans.buscar_k(X)
    k = k_forzado or _mejor_k(tablas["kmeans_k"], "silhouette")
    l, m = kmeans.entrenar(X, k)
    R["K-Means"] = dict(labels=l, modelo=m, params={"k": k}, fn=lambda Z, k=k: kmeans.entrenar(Z, k)[0])

    log.info("Jerárquico (Ward): búsqueda de k")
    tablas["jerarquico_k"] = jerarquico.buscar_k(X)
    k = k_forzado or _mejor_k(tablas["jerarquico_k"], "silhouette")
    l, m = jerarquico.entrenar(X, k)
    R["Jerárquico (Ward)"] = dict(labels=l, modelo=m, params={"k": k}, fn=lambda Z, k=k: jerarquico.entrenar(Z, k)[0])

    log.info("GMM: búsqueda de k por BIC")
    tablas["gmm_k"] = gmm.buscar_k(X)
    k = k_forzado or _mejor_k(tablas["gmm_k"], "bic", maximizar=False)
    l, m = gmm.entrenar(X, k)
    R["GMM"] = dict(labels=l, modelo=m, params={"k": k}, fn=lambda Z, k=k: gmm.entrenar(Z, k)[0])

    log.info("DBSCAN: rejilla eps x min_samples")
    tablas["dbscan_grid"] = dbscan.buscar_parametros(X)
    p = _mejor_density(tablas["dbscan_grid"], ["eps", "min_samples"])
    if p:
        eps, ms = float(p["eps"]), int(p["min_samples"])
        l, m = dbscan.entrenar(X, eps, ms)
        R["DBSCAN"] = dict(labels=l, modelo=m, params={"eps": eps, "min_samples": ms}, fn=lambda Z, e=eps, s=ms: dbscan.entrenar(Z, e, s)[0])

    log.info("HDBSCAN: rejilla min_cluster_size x min_samples")
    tablas["hdbscan_grid"] = hdbscan_model.buscar_parametros(X)
    p = _mejor_density(tablas["hdbscan_grid"], ["min_cluster_size", "min_samples"])
    if p:
        mcs, ms = int(p["min_cluster_size"]), int(p["min_samples"])
        l, m = hdbscan_model.entrenar(X, mcs, ms)
        R["HDBSCAN"] = dict(labels=l, modelo=m, params={"min_cluster_size": mcs, "min_samples": ms},
                            fn=lambda Z, a=mcs, b=ms: hdbscan_model.entrenar(Z, a, b)[0])

    filas = []
    for nombre, r in R.items():
        log.info(f"Evaluando {nombre} {r['params']}")
        met = evaluar(X, r["labels"])
        met["estabilidad_ari"] = estabilidad(X, r["fn"])
        filas.append({"modelo": nombre, "parametros": str(r["params"]), **met})
    tabla = pd.DataFrame(filas)
    tabla["elegible"] = (tabla.n_clusters.between(config.K_MIN_NEGOCIO, config.K_MAX_NEGOCIO)) & (tabla.ruido_pct <= config.MAX_RUIDO_PCT)
    return R, tabla, tablas


def seleccionar_mejor(tabla: pd.DataFrame):
    """Ranking compuesto (silhouette, Davies-Bouldin, Calinski-Harabasz, estabilidad) entre modelos elegibles."""
    t = tabla.copy()
    el = t[t.elegible] if t.elegible.any() else t.dropna(subset=["silhouette"])
    rank = (el.silhouette.rank(ascending=False) + el.davies_bouldin.rank(ascending=True)
            + el.calinski_harabasz.rank(ascending=False) + el.estabilidad_ari.rank(ascending=False)) / 4
    t["ranking_compuesto"] = rank
    return t.loc[rank.idxmin(), "modelo"], t


def matriz_ari(R):
    nombres = list(R)
    return pd.DataFrame([[adjusted_rand_score(R[a]["labels"], R[b]["labels"]) for b in nombres] for a in nombres],
                        index=nombres, columns=nombres)
