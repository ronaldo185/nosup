import io, zipfile
import streamlit as st
import utils as U
from src.reporting import pdf

U.setup("Reportes y descargas", "⬇")
U.requiere_resultados()
U.header("Reportes y descargas", "Documentos listos para presentar o archivar.")
perf = U.metrica("perfiles_segmentos.csv").sort_values("Segmento")
R, M, P = U.config.RESULTS, U.config.METRICS, U.config.PROCESSED


def dl(label, data, nombre, mime, nota):
    return st.download_button(label, data, nombre, mime, on_click=lambda: U.log.info(f"Descarga completada: {nombre}"), help=nota)


c1, c2 = st.columns(2)
with c1:
    U.card("Reporte ejecutivo (PDF)", "Resumen, calidad de datos, comparación de algoritmos, perfiles y acciones recomendadas.")
    dl("⬇ Reporte ejecutivo", pdf.reporte_ejecutivo(), "reporte_ejecutivo.pdf", "application/pdf", "Se genera con los últimos resultados")
with c2:
    U.card("Bitácora (PDF)", "Historial de ejecuciones y últimos eventos del sistema, para auditoría.")
    dl("⬇ Bitácora", pdf.reporte_bitacora(), "bitacora.pdf", "application/pdf", "Ejecuciones y eventos")

st.markdown("### Fichas por segmento")
cols = st.columns(len(perf))
for c, p in zip(cols, perf.itertuples()):
    with c: dl(f"⬇ #{p.Segmento} {p.Nombre}", pdf.ficha_segmento(int(p.Segmento)), f"ficha_segmento_{p.Segmento}.pdf", "application/pdf", p.Recomendacion)

st.markdown("### Datos y métricas")
a, b, c = st.columns(3)
with a: dl("⬇ Clientes segmentados (CSV)", (P / "clientes_segmentados.csv").read_bytes(), "clientes_segmentados.csv", "text/csv", "Una fila por cliente con su segmento")
with b: dl("⬇ Perfiles de segmentos (CSV)", (M / "perfiles_segmentos.csv").read_bytes(), "perfiles_segmentos.csv", "text/csv", "Estadísticos y recomendaciones")
with c: dl("⬇ Comparación de modelos (CSV)", (M / "comparacion_modelos.csv").read_bytes(), "comparacion_modelos.csv", "text/csv", "Métricas por algoritmo")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for f in list((R / "figures").glob("*.png")) + list(M.glob("*.csv")) + list(M.glob("*.json")):
        z.write(f, f.relative_to(R))
st.markdown("### Paquete completo")
dl("⬇ Figuras + métricas (ZIP)", buf.getvalue(), "resultados_segmentacion.zip", "application/zip", "Todas las figuras PNG y tablas de métricas")
