"""Pipeline completo: datos -> limpieza -> RFM -> modelos -> evaluación -> perfiles -> artefactos."""
import json, time, datetime as dt, joblib, numpy as np, pandas as pd
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from src import config
from src.data import carga, validacion
from src.preprocessing import limpieza, transformacion
from src.features import rfm as rfm_mod
from src.evaluation import comparacion, perfiles
from src.visualization import graficos
from src.utils import bitacora

log = bitacora.get_logger("pipeline")


def ejecutar(k_forzado=None, generar_pdf=True):
    t0, etapas, estado = time.time(), {}, "OK"
    inicio = dt.datetime.now()
    for d in (config.INTERIM, config.PROCESSED, config.METRICS, config.MODELS, config.FIGURES):
        d.mkdir(parents=True, exist_ok=True)

    def etapa(nombre):
        class _E:
            def __enter__(s): s.t = time.time(); log.info(f"▶ {nombre}")
            def __exit__(s, *a):
                etapas[nombre] = round(time.time() - s.t, 2)
                log.info(f"✔ {nombre} ({etapas[nombre]} s)" if a[0] is None else f"✖ {nombre}: {a[1]}")
        return _E()

    try:
        with etapa("1. Carga y validación"):
            raw = carga.cargar_raw()
            calidad_raw = validacion.reporte_calidad(raw)
            raw.to_csv(config.INTERIM / "retail_inspeccionado.csv", index=False)
            raw.sample(300, random_state=config.SEED).sort_index().to_csv(config.METRICS / "muestra_raw.csv", index=False)
            (config.METRICS / "calidad_raw.json").write_text(json.dumps(calidad_raw, indent=2), encoding="utf-8")
            log.info(f"{calidad_raw['filas']:,} filas, {calidad_raw['clientes_unicos']:,} clientes, nulos CustomerID={calidad_raw['nulos']['CustomerID']:,}")

        with etapa("2. Limpieza"):
            c, cancel, pasos = limpieza.limpiar(raw)
            c.to_csv(config.PROCESSED / "retail_limpio.csv", index=False)
            c.sample(300, random_state=config.SEED).sort_index().to_csv(config.METRICS / "muestra_limpia.csv", index=False)
            pasos.to_csv(config.METRICS / "limpieza_pasos.csv", index=False)
            for _, p in pasos.iterrows():
                log.info(f"  {p.paso}: -{p.eliminadas:,} filas")
            for k, v in transformacion.agregados_eda(c).items():
                v.to_csv(config.METRICS / f"eda_{k}.csv", index=False)

        with etapa("3. Ingeniería de características (RFM)"):
            rfm = rfm_mod.construir_rfm(c, cancel)
            rfm.to_csv(config.PROCESSED / "clientes_rfm.csv", index=False)
            X, scaler = transformacion.preparar_matriz(rfm)
            log.info(f"{len(rfm):,} clientes · variables: {config.FEATURES}")

        with etapa("4. Entrenamiento y comparación de modelos"):
            R, tabla, tablas = comparacion.comparar(X, k_forzado)
            mejor, tabla = comparacion.seleccionar_mejor(tabla)
            for n, t in tablas.items():
                t.to_csv(config.METRICS / f"busqueda_{n}.csv", index=False)
            tabla.to_csv(config.METRICS / "comparacion_modelos.csv", index=False)
            comparacion.matriz_ari(R).round(3).to_csv(config.METRICS / "ari_entre_modelos.csv")
            log.info(f"Modelo seleccionado: {mejor}")

        with etapa("5. Perfilamiento de segmentos"):
            lab = R[mejor]["labels"].copy()
            # reordenar ids por gasto mediano desc (0 = segmento más valioso); ruido = -1
            tmp = rfm.assign(Segmento=lab)
            orden = tmp[tmp.Segmento >= 0].groupby("Segmento").Monetary.median().sort_values(ascending=False).index
            mapa = {old: new for new, old in enumerate(orden)}; mapa[-1] = -1
            rfm["Segmento"] = pd.Series(lab).map(mapa).values
            perfil = perfiles.perfilar(rfm)
            rfm["NombreSegmento"] = rfm.Segmento.map(dict(zip(perfil.Segmento, perfil.Nombre))).fillna("Ruido / atípicos")
            pca = PCA(2, random_state=config.SEED).fit(X); coords = pca.transform(X)
            rfm["PC1"], rfm["PC2"] = coords[:, 0].round(4), coords[:, 1].round(4)
            rfm.to_csv(config.PROCESSED / "clientes_segmentados.csv", index=False)
            perfil.to_csv(config.METRICS / "perfiles_segmentos.csv", index=False)
            # clasificador para nuevos clientes (válido para cualquier algoritmo)
            ok = rfm.Segmento.values >= 0
            knn = KNeighborsClassifier(15).fit(X[ok], rfm.Segmento.values[ok])
            joblib.dump({"scaler": scaler, "clasificador": knn, "features": config.FEATURES, "pca_var": [float(v) for v in pca.explained_variance_ratio_],
                         "nombres": dict(zip(perfil.Segmento, perfil.Nombre))}, config.MODELS / "clasificador.joblib")
            joblib.dump(R[mejor]["modelo"], config.MODELS / "modelo_final.joblib")
            for p in perfil.itertuples():
                log.info(f"  Segmento {p.Segmento} · {p.Nombre}: {p.Clientes:,} clientes, {p.PctIngresos:.1f}% ingresos")

        with etapa("6. Figuras"):
            graficos.seleccion_k(tablas["kmeans_k"]); graficos.comparacion_modelos(tabla)
            graficos.pca_segmentos(coords, rfm.Segmento.values, dict(zip(perfil.Segmento, perfil.Nombre)), pca.explained_variance_ratio_)
            graficos.tamano_vs_ingresos(perfil); graficos.heatmap_perfil(perfil); graficos.distribuciones_rfm(rfm)

        fila = tabla[tabla.modelo == mejor].iloc[0]
        resumen = {"clientes": len(rfm), "facturas": int(c.InvoiceNo.nunique()), "ingresos": float(c.TotalPrice.sum()),
                   "filas_raw": calidad_raw["filas"], "filas_limpias": len(c), "fecha_min": str(c.InvoiceDate.min()),
                   "fecha_max": str(c.InvoiceDate.max()), "modelo_final": mejor, "modelo_final_params": str(R[mejor]["params"]),
                   "n_segmentos": int(rfm[rfm.Segmento >= 0].Segmento.nunique()), "silhouette_final": float(fila.silhouette),
                   "davies_bouldin_final": float(fila.davies_bouldin), "calinski_final": float(fila.calinski_harabasz),
                   "estabilidad_final": float(fila.estabilidad_ari), "pct_ruido_final": float(fila.ruido_pct),
                   "features": config.FEATURES, "pca_var": [float(v) for v in pca.explained_variance_ratio_], "fecha_referencia_recencia": str(c.InvoiceDate.max().normalize() + pd.Timedelta(days=1))}
        (config.METRICS / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

        if generar_pdf:
            with etapa("7. Reportes PDF + documentación"):
                from src.reporting import pdf, docs
                (config.RESULTS / "reporte_ejecutivo.pdf").write_bytes(pdf.reporte_ejecutivo())
                docs.escribir_resultados()
    except Exception as e:
        estado = f"ERROR: {e}"; log.exception("Fallo en el pipeline"); raise
    finally:
        dur = round(time.time() - t0, 1)
        bitacora.guardar_ejecucion({"inicio": inicio.isoformat(), "duracion_s": dur, "estado": estado, "etapas": etapas,
                                    "k_forzado": k_forzado, **({"modelo_final": mejor, "n_segmentos": resumen["n_segmentos"]} if estado == "OK" else {})})
        log.info(f"Pipeline finalizado: {estado} en {dur} s")
    return resumen
