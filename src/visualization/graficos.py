"""Gráficos estáticos (matplotlib) usados en los reportes PDF."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd
from src import config

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#CBD5E1", "axes.labelcolor": "#334155", "xtick.color": "#475569",
                     "ytick.color": "#475569", "axes.titleweight": "bold", "axes.titlesize": 11, "figure.dpi": 150})
P = config.PALETA


def _guardar(fig, nombre):
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    ruta = config.FIGURES / nombre
    fig.savefig(ruta, bbox_inches="tight", facecolor="white"); plt.close(fig)
    return ruta


def seleccion_k(tk):
    fig, ax = plt.subplots(1, 3, figsize=(10, 2.8))
    for a, c, t in zip(ax, ["inercia", "silhouette", "davies_bouldin"], ["Inercia (codo)", "Silhouette ↑", "Davies-Bouldin ↓"]):
        a.plot(tk.k, tk[c], marker="o", color=P[0]); a.set_title(t); a.set_xlabel("k")
    return _guardar(fig, "seleccion_k_kmeans.png")


def comparacion_modelos(tabla):
    fig, ax = plt.subplots(1, 4, figsize=(11, 2.9))
    for a, c, t in zip(ax, ["silhouette", "davies_bouldin", "calinski_harabasz", "estabilidad_ari"],
                       ["Silhouette ↑", "Davies-Bouldin ↓", "Calinski-Harabasz ↑", "Estabilidad (ARI) ↑"]):
        a.barh(tabla.modelo, tabla[c].fillna(0), color=P[:len(tabla)]); a.set_title(t); a.invert_yaxis()
        if a is not ax[0]: a.set_yticklabels([])
    return _guardar(fig, "comparacion_modelos.png")


def pca_segmentos(coords, seg, nombres, varianza):
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    for i, s in enumerate(sorted(set(seg))):
        m = seg == s
        ax.scatter(coords[m, 0], coords[m, 1], s=9, alpha=.65, color="#94A3B8" if s == -1 else P[i % 8],
                   label="Ruido" if s == -1 else nombres.get(s, s))
    ax.set_xlabel(f"PC1 ({varianza[0]:.0%})"); ax.set_ylabel(f"PC2 ({varianza[1]:.0%})"); ax.legend(fontsize=7, frameon=False)
    ax.set_title("Segmentos en el plano PCA")
    return _guardar(fig, "pca_segmentos.png")


def tamano_vs_ingresos(perfil):
    fig, ax = plt.subplots(figsize=(6.2, 3.2)); x = np.arange(len(perfil)); w = .38
    ax.bar(x - w / 2, perfil.PctClientes, w, label="% clientes", color=P[1])
    ax.bar(x + w / 2, perfil.PctIngresos, w, label="% ingresos", color=P[0])
    ax.set_xticks(x); ax.set_xticklabels(perfil.Nombre, rotation=20, ha="right", fontsize=7); ax.legend(frameon=False)
    ax.set_title("Peso de cada segmento: clientes vs ingresos")
    return _guardar(fig, "tamano_vs_ingresos.png")


def heatmap_perfil(perfil):
    cols = ["Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts"]
    z = (perfil[cols] - perfil[cols].min()) / (perfil[cols].max() - perfil[cols].min() + 1e-9)
    fig, ax = plt.subplots(figsize=(6.2, 3)); im = ax.imshow(z.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=8); ax.set_yticks(range(len(perfil)))
    ax.set_yticklabels(perfil.Nombre, fontsize=8)
    for i in range(len(perfil)):
        for j, c in enumerate(cols): ax.text(j, i, f"{perfil[c].iloc[i]:,.0f}", ha="center", va="center", fontsize=7,
                                             color="white" if z.values[i, j] > .55 else "#1E293B")
    ax.set_title("Perfil mediano por segmento"); [s.set_visible(False) for s in ax.spines.values()]
    return _guardar(fig, "heatmap_perfil.png")


def distribuciones_rfm(rfm):
    fig, ax = plt.subplots(1, 3, figsize=(10, 2.6))
    for a, c, col in zip(ax, ["Recency", "Frequency", "Monetary"], P):
        a.hist(np.log1p(rfm[c]), bins=40, color=col, alpha=.9); a.set_title(f"log(1+{c})")
    return _guardar(fig, "distribuciones_rfm.png")
