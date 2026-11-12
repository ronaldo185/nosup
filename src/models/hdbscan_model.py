import itertools, pandas as pd
try:
    from sklearn.cluster import HDBSCAN        # scikit-learn >= 1.3
except ImportError:                             # pragma: no cover
    from hdbscan import HDBSCAN
from src.evaluation.metricas import evaluar


def entrenar(X, min_cluster_size, min_samples):
    m = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples).fit(X)
    return m.labels_, m


def buscar_parametros(X, mcs_grid=(20, 40, 60, 100, 150), ms_grid=(5, 10, 20)):
    filas = []
    for mcs, ms in itertools.product(mcs_grid, ms_grid):
        l, _ = entrenar(X, mcs, ms)
        filas.append({"min_cluster_size": mcs, "min_samples": ms, **evaluar(X, l)})
    return pd.DataFrame(filas)
