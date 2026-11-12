import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from src import config


def evaluar(X, labels) -> dict:
    """Métricas internas. El ruido (-1) se excluye del cálculo y se reporta aparte."""
    labels = np.asarray(labels)
    mask = labels != -1
    ncl = len(set(labels[mask]))
    out = {"n_clusters": ncl, "ruido_pct": round(100 * (~mask).mean(), 2),
           "silhouette": np.nan, "davies_bouldin": np.nan, "calinski_harabasz": np.nan}
    if ncl >= 2 and mask.sum() > ncl:
        out.update(silhouette=silhouette_score(X[mask], labels[mask]),
                   davies_bouldin=davies_bouldin_score(X[mask], labels[mask]),
                   calinski_harabasz=calinski_harabasz_score(X[mask], labels[mask]))
    return out


def estabilidad(X, entrenar_fn, n=6, frac=0.8, seed=config.SEED) -> float:
    """ARI medio entre ajustes sobre submuestras (80%) comparados en los puntos comunes."""
    rng = np.random.default_rng(seed)
    aris = []
    for _ in range(n):
        ia = rng.choice(len(X), int(frac * len(X)), replace=False)
        ib = rng.choice(len(X), int(frac * len(X)), replace=False)
        la, lb = dict(zip(ia, entrenar_fn(X[ia]))), dict(zip(ib, entrenar_fn(X[ib])))
        comun = np.intersect1d(ia, ib)
        aris.append(adjusted_rand_score([la[i] for i in comun], [lb[i] for i in comun]))
    return float(np.mean(aris))
