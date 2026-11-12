import itertools, numpy as np, pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from src import config
from src.evaluation.metricas import evaluar


def entrenar(X, eps, min_samples):
    m = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    return m.labels_, m


def k_distancias(X, k=10):
    d, _ = NearestNeighbors(n_neighbors=k).fit(X).kneighbors(X)
    return np.sort(d[:, -1])


def buscar_parametros(X, eps_grid=None, ms_grid=(5, 10, 15, 20)):
    eps_grid = eps_grid if eps_grid is not None else np.round(np.arange(0.3, 1.31, 0.1), 2)
    filas = []
    for eps, ms in itertools.product(eps_grid, ms_grid):
        l, _ = entrenar(X, eps, ms)
        filas.append({"eps": eps, "min_samples": ms, **evaluar(X, l)})
    return pd.DataFrame(filas)
