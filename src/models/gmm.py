import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from src import config


def entrenar(X, k, seed=config.SEED):
    m = GaussianMixture(n_components=k, covariance_type="full", n_init=5, random_state=seed).fit(X)
    return m.predict(X), m


def buscar_k(X, ks=config.K_RANGE):
    filas = []
    for k in ks:
        l, m = entrenar(X, k)
        filas.append({"k": k, "bic": m.bic(X), "aic": m.aic(X), "silhouette": silhouette_score(X, l)})
    return pd.DataFrame(filas)
