"""Generación de reportes PDF (ReportLab): ejecutivo y ficha por segmento."""
import io, json, datetime as dt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from src import config

INDIGO, SLATE = colors.HexColor("#4F46E5"), colors.HexColor("#334155")
_ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_ss["Heading1"], fontSize=20, textColor=SLATE, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=_ss["Heading2"], fontSize=13, textColor=INDIGO, spaceBefore=12, spaceAfter=4)
B = ParagraphStyle("B", parent=_ss["BodyText"], fontSize=9.5, leading=13.5, textColor=SLATE)
SM = ParagraphStyle("SM", parent=B, fontSize=8, textColor=colors.HexColor("#64748B"))


def _cargar():
    m = config.METRICS
    return (json.loads((m / "resumen.json").read_text(encoding="utf-8")), pd.read_csv(m / "comparacion_modelos.csv"),
            pd.read_csv(m / "perfiles_segmentos.csv"), pd.read_csv(m / "limpieza_pasos.csv"))


def _tabla(df, anchos=None, fs=7.5):
    data = [list(df.columns)] + df.astype(str).values.tolist()
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), INDIGO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), fs), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#E2E8F0")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def _img(nombre, ancho=16):
    p = config.FIGURES / nombre
    if not p.exists(): return Spacer(1, 1)
    from PIL import Image as PI
    w, h = PI.open(p).size
    return Image(str(p), width=ancho * cm, height=ancho * cm * h / w)


def _pie(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor("#94A3B8"))
    c.drawString(2 * cm, 1.2 * cm, "Sistema de Segmentación de Clientes · UCI Online Retail")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {d.page}"); c.restoreState()


def _doc(buf, titulo):
    return SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                             bottomMargin=2 * cm, title=titulo, author="Sistema de Segmentación")


def reporte_ejecutivo() -> bytes:
    res, comp, perf, limp = _cargar()
    buf = io.BytesIO(); doc = _doc(buf, "Reporte ejecutivo de segmentación"); s = []
    s += [Paragraph("Reporte ejecutivo", H1), Paragraph("Segmentación de clientes mediante Machine Learning no supervisado", B),
          Paragraph(f"Generado: {dt.datetime.now():%Y-%m-%d %H:%M} · Periodo: {res['fecha_min'][:10]} a {res['fecha_max'][:10]}", SM),
          Paragraph("1. Resumen", H2),
          Paragraph(f"Se analizaron <b>{res['clientes']:,}</b> clientes con <b>{res['facturas']:,}</b> facturas y ingresos totales de "
                    f"<b>£{res['ingresos']:,.0f}</b>. El mejor modelo según el ranking compuesto fue <b>{res['modelo_final']}</b> "
                    f"({res['modelo_final_params']}), que identifica <b>{res['n_segmentos']}</b> segmentos con silhouette de "
                    f"<b>{res['silhouette_final']:.3f}</b>.", B),
          Paragraph("2. Calidad y limpieza de datos", H2), Paragraph(
              f"Se partió de {res['filas_raw']:,} registros y quedaron {res['filas_limpias']:,} compras válidas. Cada paso fue registrado:", B),
          Spacer(1, 4), _tabla(limp[["paso", "filas_antes", "filas_despues", "eliminadas"]], [6 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm], 8),
          _img("distribuciones_rfm.png"),
          Paragraph("3. Comparación de algoritmos", H2),
          Paragraph("Se compararon K-Means, Jerárquico (Ward), GMM, DBSCAN y HDBSCAN con métricas internas y estabilidad "
                    "(ARI en submuestras). Se consideran elegibles los modelos con 4-8 grupos y ≤10% de ruido.", B), Spacer(1, 4),
          _tabla(comp[["modelo", "n_clusters", "ruido_pct", "silhouette", "davies_bouldin", "calinski_harabasz", "estabilidad_ari", "elegible"]].round(3),
                 fs=7), _img("comparacion_modelos.png"), PageBreak(),
          Paragraph("4. Segmentos de clientes", H2), _img("pca_segmentos.png", 12), _img("tamano_vs_ingresos.png", 12), _img("heatmap_perfil.png", 12),
          PageBreak(), Paragraph("5. Perfiles y acciones recomendadas", H2)]
    for _, r in perf.iterrows():
        s += [Paragraph(f"<b>{r.Nombre}</b> — {int(r.Clientes):,} clientes ({r.PctClientes:.1f}%) · {r.PctIngresos:.1f}% de los ingresos", B),
              Paragraph(f"Mediana: recencia {r.Recency:.0f} días · frecuencia {r.Frequency:.0f} · gasto £{r.Monetary:,.0f} · "
                        f"ticket £{r.AvgTicket:,.0f}", SM), Paragraph(f"<i>Acción:</i> {r.Recomendacion}", B), Spacer(1, 6)]
    from src.evaluation import conclusiones as C
    H_ = C.hechos(); CO = C.conclusiones(H_); MB = C.mejor_modelo(H_)
    cv = lambda t: __import__("re").sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    s += [Paragraph("6. Mejor modelo y conclusiones", H2), Paragraph(cv(MB["veredicto"]), B), Spacer(1, 4)]
    s += [Paragraph(f"{i}. {cv(c)}", B) for i, c in enumerate(CO["conclusiones"], 1)]
    s += [Paragraph("Hallazgos principales", H2)] + [Paragraph(f"<b>{t}:</b> {cv(d)}", B) for t, d in C.hallazgos(H_)]
    s += [Paragraph("7. Limitaciones", H2)] + [Paragraph("• " + x, B) for x in CO["limitaciones"]]

    doc.build(s, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()


def ficha_segmento(segmento_id: int) -> bytes:
    res, _, perf, _ = _cargar()
    r = perf[perf.Segmento == segmento_id].iloc[0]
    cl = pd.read_csv(config.PROCESSED / "clientes_segmentados.csv"); cl = cl[cl.Segmento == segmento_id]
    buf = io.BytesIO(); doc = _doc(buf, f"Ficha - {r.Nombre}")
    top = cl.sort_values("Monetary", ascending=False).head(10)[["CustomerID", "Recency", "Frequency", "Monetary", "Country"]].round(1)
    paises = cl.Country.value_counts().head(5).rename_axis("País").reset_index(name="Clientes")
    s = [Paragraph(f"Ficha de segmento: {r.Nombre}", H1), Paragraph(f"Modelo: {res['modelo_final']} · Segmento #{segmento_id}", SM),
         Paragraph("Resumen", H2),
         Paragraph(f"{int(r.Clientes):,} clientes ({r.PctClientes:.1f}% de la base) generan £{r.Ingresos:,.0f} "
                   f"({r.PctIngresos:.1f}% de los ingresos).", B), Spacer(1, 6),
         _tabla(pd.DataFrame({"Indicador": ["Recencia (mediana, días)", "Frecuencia (mediana)", "Gasto total (mediana)", "Ticket medio (mediana)",
                                           "Productos distintos (mediana)", "Tasa de devolución"],
                              "Valor": [f"{r.Recency:.0f}", f"{r.Frequency:.0f}", f"£{r.Monetary:,.0f}", f"£{r.AvgTicket:,.0f}",
                                        f"{r.UniqueProducts:.0f}", f"{r.ReturnRate:.1%}"]}), [8 * cm, 4 * cm], 9),
         Paragraph("Acción recomendada", H2), Paragraph(str(r.Recomendacion), B),
         Paragraph("Principales países", H2), _tabla(paises, [8 * cm, 4 * cm], 9),
         Paragraph("Top 10 clientes por gasto", H2), _tabla(top, fs=8)]
    doc.build(s, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()


def reporte_bitacora() -> bytes:
    from src.utils.bitacora import leer_ejecuciones, leer_log
    buf = io.BytesIO(); doc = _doc(buf, "Bitácora del sistema")
    s = [Paragraph("Bitácora del sistema", H1), Paragraph("Historial de ejecuciones", H2)]
    ej = leer_ejecuciones()
    if ej:
        df = pd.DataFrame([{"Inicio": e.get("inicio", "")[:19], "Duración (s)": e.get("duracion_s"), "Modelo": e.get("modelo_final"),
                            "Segmentos": e.get("n_segmentos"), "Estado": e.get("estado")} for e in ej])
        s.append(_tabla(df, fs=8))
    s.append(Paragraph("Últimos eventos", H2))
    mono = ParagraphStyle("mono", parent=SM, fontName="Courier", fontSize=6.5, leading=8)
    s += [Paragraph(l.replace("&", "&amp;").replace("<", "&lt;"), mono) for l in leer_log(150)]
    doc.build(s, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()
