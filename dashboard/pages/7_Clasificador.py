import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import utils as U

U.setup("Clasificador de clientes", "✦")
U.requiere_resultados()
U.header("Clasificador de clientes", "Asigna un cliente nuevo (o hipotético) a uno de los segmentos descubiertos.")
perf = U.metrica("perfiles_segmentos.csv").sort_values("Segmento")
art = joblib.load(U.config.MODELS / "clasificador.joblib")

a, b = st.columns([1, 1.2])
with a:
    st.markdown("**Datos del cliente**")
    r = st.number_input("Recencia (días desde su última compra)", 1, 400, 30)
    fr = st.number_input("Frecuencia (nº de facturas)", 1, 300, 4)
    m = st.number_input("Gasto total (£)", 1.0, 300000.0, 1200.0, step=50.0)
    pr = st.number_input("Productos distintos comprados", 1, 2000, 40)
    tk = m / fr
    st.caption(f"Ticket medio calculado: £{tk:,.0f}")
    ok = st.button("Clasificar", type="primary")
if ok:
    fila = pd.DataFrame([{"Recency": r, "Frequency": fr, "Monetary": m, "AvgTicket": tk, "UniqueProducts": pr}])[art["features"]]
    X = art["scaler"].transform(np.log1p(fila))
    prob = art["clasificador"].predict_proba(X)[0]; clases = art["clasificador"].classes_
    s = int(clases[prob.argmax()]); nombre = art["nombres"][s]
    U.log.info(f"Clasificación manual: R={r} F={fr} M={m:.0f} -> segmento {s} ({nombre})")
    with b:
        st.markdown(f"<div class='banner'>Segmento asignado: <b>{nombre}</b> (#{s}) · confianza {prob.max():.0%}</div>", unsafe_allow_html=True)
        U.card("Acción recomendada", perf[perf.Segmento == s].Recomendacion.iloc[0])
        f = go.Figure(go.Bar(x=[art["nombres"][int(c)] for c in clases], y=prob, marker_color=U.C1))
        f.update_layout(title="Probabilidad por segmento", yaxis_tickformat=".0%"); U.grafico(f, 300, False)
        ref = perf[perf.Segmento == s].iloc[0]
        st.dataframe(pd.DataFrame({"Variable": ["Recencia", "Frecuencia", "Gasto", "Ticket"], "Este cliente": [r, fr, round(m), round(tk)],
                                   f"Mediana del segmento": [ref.Recency, ref.Frequency, ref.Monetary, ref.AvgTicket]}), hide_index=True, use_container_width=True)
else:
    with b: st.info("Introduce los datos y pulsa **Clasificar**. Se usa el mismo escalado (log + estandarización) y un clasificador k-NN entrenado sobre los segmentos finales.")
