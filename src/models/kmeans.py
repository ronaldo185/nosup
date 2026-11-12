import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from src import config


def entrenar(X, k, seed=config.SEED):
    m = KMeans(n_clusters=k, n_init=20, random_state=seed).fit(X)
    return m.labels_, m


def buscar_k(X, ks=config.K_RANGE):
    filas = []
    for k in ks:
        l, m = entrenar(X, k)
        filas.append({"k": k, "inercia": m.inertia_, "silhouette": silhouette_score(X, l),
                      "davies_bouldin": davies_bouldin_score(X, l), "calinski_harabasz": calinski_harabasz_score(X, l)})
    return pd.DataFrame(filas)
