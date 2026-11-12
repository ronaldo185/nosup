"""Genera docs/resultados.md a partir de las métricas reales."""
import json, pandas as pd
from src import config


def escribir_resultados():
    m = config.METRICS
    r = json.loads((m / "resumen.json").read_text(encoding="utf-8"))
    comp, perf = pd.read_csv(m / "comparacion_modelos.csv"), pd.read_csv(m / "perfiles_segmentos.csv")
    md = ["# Resultados", "", "*Documento generado automáticamente por el pipeline.*", "",
          f"- Periodo: {r['fecha_min'][:10]} → {r['fecha_max'][:10]}", f"- Clientes segmentados: **{r['clientes']:,}**",
          f"- Ingresos analizados: **£{r['ingresos']:,.0f}**", f"- Modelo final: **{r['modelo_final']}** `{r['modelo_final_params']}`",
          f"- Silhouette: {r['silhouette_final']:.3f} · Davies-Bouldin: {r['davies_bouldin_final']:.3f} · Estabilidad (ARI): {r['estabilidad_final']:.3f}", "",
          "## Comparación de algoritmos", "", comp[["modelo", "parametros", "n_clusters", "ruido_pct", "silhouette", "davies_bouldin",
                                                    "calinski_harabasz", "estabilidad_ari", "elegible"]].round(3).to_markdown(index=False)
          if _tiene_tabulate() else comp.round(3).to_string(index=False), "", "## Segmentos", ""]
    for _, p in perf.iterrows():
        md += [f"### {p.Nombre} (segmento {int(p.Segmento)})",
               f"- {int(p.Clientes):,} clientes ({p.PctClientes:.1f}%), {p.PctIngresos:.1f}% de ingresos",
               f"- Mediana: recencia {p.Recency:.0f} d, frecuencia {p.Frequency:.0f}, gasto £{p.Monetary:,.0f}", f"- Acción: {p.Recomendacion}", ""]
    (config.DOCS / "resultados.md").write_text("\n".join(md), encoding="utf-8")


def _tiene_tabulate():
    try: import tabulate; return True
    except ImportError: return False
