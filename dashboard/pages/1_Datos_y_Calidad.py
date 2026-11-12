import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils as U
from src.data import diccionario

U.setup("Datos y calidad", "▦")
U.requiere_resultados()
U.header("Datos y calidad", "Qué entró al sistema, qué se eliminó y por qué. Incluye diccionario y muestra del dataset.")
N = U.notas()
raw, pasos, res = U.metrica("calidad_raw.json"), U.metrica("limpieza_pasos.csv"), U.metrica("resumen.json")

U.kpi_row([("Registros originales", f"{raw['filas']:,}", f"{raw['columnas']} columnas"), ("Compras válidas", f"{res['filas_limpias']:,}",
           f"{100 * res['filas_limpias'] / raw['filas']:.1f}% conservado"), ("Sin CustomerID", f"{raw['nulos']['CustomerID']:,}",
           f"{100 * raw['nulos']['CustomerID'] / raw['filas']:.1f}% del total"), ("Cancelaciones", f"{raw['cancelaciones']:,}", "facturas 'C'"),
           ("Duplicados", f"{raw['duplicados_exactos']:,}", "filas exactas")])
st.write("")
t1, t2, t3, t4, t5 = st.tabs(["Limpieza", "Ventas en el tiempo", "Países y productos", "Muestra del dataset", "Diccionario"])

with t1:
    a, b = st.columns([1.2, 1])
    with a:
        f = go.Figure(go.Waterfall(x=["Original"] + list(pasos.paso) + ["Final"], measure=["absolute"] + ["relative"] * len(pasos) + ["total"],
                                   y=[raw["filas"]] + [-int(x) for x in pasos.eliminadas] + [0], decreasing=dict(marker_color=U.C5),
                                   increasing=dict(marker_color=U.C3), totals=dict(marker_color=U.C1)))
        f.update_layout(title="Filas tras cada paso de limpieza"); f.update_xaxes(tickangle=-25)
        U.grafico(f, 400, False); U.nota(N["d_waterfall"])
    with b:
        nul = {k: v for k, v in raw["nulos"].items() if v > 0}
        f = px.bar(x=list(nul.values()), y=list(nul.keys()), orientation="h", title="Valores nulos (dataset original)")
        f.update_traces(marker_color=U.C4); U.grafico(f, 200, False); U.nota(N["d_nulos"])
    st.dataframe(pasos.rename(columns={"paso": "Paso", "filas_antes": "Antes", "filas_despues": "Después", "eliminadas": "Eliminadas", "motivo": "Motivo"}),
                 use_container_width=True, hide_index=True)

with t2:
    m = U.metrica("eda_ventas_mensuales.csv")
    f = go.Figure()
    f.add_bar(x=m.Mes, y=m.Ingresos, name="Ingresos (£)", marker_color=U.SUAVE)
    f.add_scatter(x=m.Mes, y=m.Clientes, name="Clientes activos", yaxis="y2", line=dict(color=U.C1, width=3))
    f.update_layout(title="Ingresos mensuales y clientes activos", yaxis2=dict(overlaying="y", side="right", showgrid=False))
    U.grafico(f, 380); U.nota(N["d_mensual"])
    hd = U.metrica("eda_dia_hora.csv")
    dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    piv = hd.pivot(index="Dia", columns="Hora", values="Facturas").reindex(dias).fillna(0)
    fig = px.imshow(piv, color_continuous_scale=U.ESCALA, aspect="auto", title="Facturas por día y hora", labels=dict(color="Facturas"))
    U.grafico(fig, 320, False); U.nota(N["d_horas"])

with t3:
    a, b = st.columns(2)
    p = U.metrica("eda_ventas_pais.csv").head(10)
    f = px.bar(p.iloc[::-1], x="Ingresos", y="Country", orientation="h", title="Top 10 países por ingresos"); f.update_traces(marker_color=U.C1)
    with a: U.grafico(f, 420, False); U.nota(N["d_pais"])
    pr = U.metrica("eda_top_productos.csv").head(10)
    f = px.bar(pr.iloc[::-1], x="Ingresos", y="Description", orientation="h", title="Top 10 productos por ingresos"); f.update_traces(marker_color=U.C2)
    with b: U.grafico(f, 420, False); U.nota(N["d_prod"])

with t4:
    st.markdown("Muestra aleatoria de **300 filas** (semilla fija) del dataset antes y después de la limpieza. No se modifica el archivo original.")
    vista = st.radio("Conjunto", ["Original (sin limpiar)", "Limpio (compras válidas)", "Clientes (resultado RFM + segmento)"], horizontal=True)
    if vista.startswith("Original"):
        df = U.metrica("muestra_raw.csv"); st.caption("Fíjate en los CustomerID vacíos, las facturas 'C…' y las cantidades negativas: se tratan en la limpieza.")
    elif vista.startswith("Limpio"):
        df = U.metrica("muestra_limpia.csv"); st.caption("Solo compras válidas con cliente identificado; incluye la columna derivada TotalPrice.")
    else:
        df = U.clientes().sample(300, random_state=42).sort_values("CustomerID"); st.caption("Una fila por cliente: variables RFM, comerciales y segmento asignado.")
    n = st.slider("Filas a mostrar", 10, 300, 50, step=10)
    st.dataframe(df.head(n), use_container_width=True, hide_index=True, height=380)
    a, b = st.columns(2)
    a.markdown(f"**Forma de la muestra:** {df.shape[0]} filas × {df.shape[1]} columnas")
    st.download_button("⬇ Descargar muestra (CSV)", df.to_csv(index=False).encode("utf-8"), "muestra_dataset.csv", "text/csv")
    with st.expander("Resumen estadístico de las columnas numéricas"):
        st.dataframe(df.describe().T.round(2), use_container_width=True)

with t5:
    muestra = U.metrica("muestra_raw.csv")
    ej = {c: str(muestra[c].dropna().iloc[0]) for c in muestra.columns}
    orig = pd.DataFrame([(v, t, d, ej.get(v, ""), f"{raw['nulos'].get(v, 0):,}") for v, t, d in diccionario.ORIGINAL],
                        columns=["Variable", "Tipo", "Descripción", "Ejemplo", "Nulos (original)"])
    st.markdown("**Variables originales (UCI Online Retail)**")
    st.dataframe(orig, use_container_width=True, hide_index=True)
    st.markdown("**Variables derivadas por el sistema**")
    der = pd.DataFrame([(v, t, d, "Sí" if u else "—") for v, t, d, u in diccionario.DERIVADAS], columns=["Variable", "Tipo", "Descripción", "Usada para agrupar"])
    st.dataframe(der, use_container_width=True, hide_index=True)
    U.nota("Para agrupar se usaron **Recency, Frequency, Monetary, AvgTicket y UniqueProducts** (con log(1+x) y estandarización). "
           "El resto se emplea para interpretar los segmentos.")
