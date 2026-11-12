import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from src import config


def entrenar(X, k):
    m = AgglomerativeClustering(n_clusters=k, linkage="ward").fit(X)
    return m.labels_, m


def buscar_k(X, ks=config.K_RANGE):
    return pd.DataFrame([{"k": k, "silhouette": silhouette_score(X, entrenar(X, k)[0])} for k in ks])
