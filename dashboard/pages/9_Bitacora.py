import pandas as pd
import plotly.express as px
import streamlit as st
import utils as U
from src.utils import bitacora

U.setup("Bitácora", "☰")
U.header("Bitácora del sistema", "Trazabilidad de ejecuciones, decisiones y uso del dashboard.")
t1, t2, t3 = st.tabs(["Ejecuciones", "Registro de eventos", "Re-ejecutar pipeline"])

with t1:
    ej = bitacora.leer_ejecuciones()
    if not ej:
        st.info("Todavía no hay ejecuciones registradas.")
    else:
        df = pd.DataFrame([{"Inicio": e["inicio"][:19].replace("T", " "), "Duración (s)": e["duracion_s"], "Estado": e["estado"],
                            "Modelo": e.get("modelo_final", "–"), "Segmentos": e.get("n_segmentos", "–"), "k forzado": e.get("k_forzado") or "auto"} for e in ej])
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
        et = pd.DataFrame(ej[-1]["etapas"].items(), columns=["Etapa", "Segundos"])
        f = px.bar(et.iloc[::-1], x="Segundos", y="Etapa", orientation="h", title="Duración por etapa (última ejecución)"); f.update_traces(marker_color=U.C1)
        U.grafico(f, 340, False)

with t2:
    lineas = bitacora.leer_log(3000)
    filas = [l.split(" | ", 3) for l in lineas if l.count(" | ") >= 3]
    d = pd.DataFrame(filas, columns=["Fecha", "Nivel", "Módulo", "Mensaje"]); d["Nivel"] = d.Nivel.str.strip(); d["Módulo"] = d["Módulo"].str.strip()
    a, b, c = st.columns([1, 1, 2])
    with a: niv = st.multiselect("Nivel", sorted(d.Nivel.unique()), default=sorted(d.Nivel.unique()))
    with b: mod = st.multiselect("Módulo", sorted(d["Módulo"].unique()), default=sorted(d["Módulo"].unique()))
    with c: txt = st.text_input("Buscar en mensajes")
    v = d[d.Nivel.isin(niv) & d["Módulo"].isin(mod)]
    if txt: v = v[v.Mensaje.str.contains(txt, case=False, regex=False)]
    st.dataframe(v.iloc[::-1], use_container_width=True, hide_index=True, height=420)
    st.download_button("⬇ Descargar bitácora (.log)", "\n".join(lineas).encode("utf-8"), "bitacora.log", "text/plain")

with t3:
    st.markdown("Vuelve a ejecutar todo el flujo (carga → limpieza → RFM → modelos → reportes). Tarda alrededor de 1-2 minutos.")
    modo = st.radio("Número de segmentos", ["Automático (recomendado)", "Forzar k"], horizontal=True)
    k = st.slider("k", 3, 8, 4) if modo.startswith("Forzar") else None
    if st.button("▶ Ejecutar pipeline", type="primary"):
        from src.pipeline import ejecutar
        U.log.info(f"Pipeline lanzado desde el dashboard (k={k or 'auto'})")
        with st.spinner("Ejecutando pipeline…"):
            try:
                r = ejecutar(k)
                st.cache_data.clear()
                st.success(f"Listo: {r['n_segmentos']} segmentos con {r['modelo_final']}. Recarga las demás páginas para ver los cambios.")
            except Exception as e:
                st.error(f"El pipeline falló: {e}")
