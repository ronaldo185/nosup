"""Utilidades compartidas del dashboard: estilo, carga de datos y componentes."""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from src import config
from src.utils.bitacora import get_logger

log = get_logger("dashboard")
import os as _os
_OSC = _os.environ.get("DASH_TEMA", "oscuro").lower() != "claro"
if _OSC:   # tema oscuro (índigo)
    PALETA = ["#818CF8", "#38BDF8", "#34D399", "#FBBF24", "#F87171", "#A78BFA", "#2DD4BF", "#94A3B8"]
    SUAVE, RUIDO = "#2A3042", "#4B5563"
    ESCALA, ESCALA_DIV = [[0, "#12151C"], [1, "#818CF8"]], [[0, "#F87171"], [0.5, "#12151C"], [1, "#818CF8"]]
    PLANTILLA, TXT, TXT2, GRID, HOVER = "plotly_dark", "#9CA3AF", "#D1D5DB", "#171B24", "#171B24"
else:      # tema claro editorial (esmeralda)
    PALETA = ["#059669", "#0369A1", "#D97706", "#BE123C", "#4338CA", "#0F766E", "#B45309", "#78716C"]
    SUAVE, RUIDO = "#D6D3D1", "#A8A29E"
    ESCALA, ESCALA_DIV = [[0, "#FBFAF7"], [1, "#059669"]], [[0, "#BE123C"], [0.5, "#FBFAF7"], [1, "#059669"]]
    PLANTILLA, TXT, TXT2, GRID, HOVER = "plotly_white", "#57534E", "#1C1917", "#EDEBE6", "#FFFFFF"
C1, C2, C3, C4, C5, C6 = PALETA[0], PALETA[1], PALETA[2], PALETA[3], PALETA[4], PALETA[5]

CSS_OSCURO = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, button, input { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0B0D12; }
.block-container { padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1180px; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
section[data-testid="stSidebar"] { background: #0E1118; border-right: 1px solid #171B24; }
h1 { font-weight: 600 !important; letter-spacing: -0.02em; color: #F3F4F6; font-size: 1.7rem !important; margin-bottom: .1rem; }
h2, h3 { font-weight: 500 !important; letter-spacing: -0.01em; color: #D1D5DB; font-size: 1.05rem !important; margin-top: 1.6rem; }
.sub { color: #6B7280; font-size: .88rem; margin-bottom: 1.6rem; }
.kpi { background: #12151C; border-radius: 12px; padding: 16px 18px; }
.kpi .l { font-size: .68rem; text-transform: uppercase; letter-spacing: .09em; color: #6B7280; font-weight: 500; }
.kpi .v { font-size: 1.6rem; font-weight: 600; color: #F3F4F6; margin-top: 4px; line-height: 1.15; }
.kpi .d { font-size: .76rem; color: #6B7280; margin-top: 3px; }
.card { background: #12151C; border-radius: 12px; padding: 16px 18px; margin-bottom: 12px; }
.card h4 { margin: 0 0 6px 0; font-size: .95rem; font-weight: 500; color: #F3F4F6; }
.card p { margin: 6px 0 0 0; color: #9CA3AF; font-size: .84rem; line-height: 1.55; }
.pill { display: inline-block; padding: 0; margin-right: 12px; font-size: .72rem; color: #818CF8; font-weight: 500; }
.banner { border-left: 2px solid #818CF8; padding: 6px 0 6px 14px; color: #9CA3AF; font-size: .9rem; margin: .4rem 0 1.2rem 0; }
.banner b { color: #E5E7EB; font-weight: 500; }
div[data-testid="stTabs"] button { font-weight: 400; color: #6B7280; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #F3F4F6; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; border: 1px solid #232836; background: #12151C; color: #D1D5DB; font-weight: 400; }
.stDownloadButton > button:hover, .stButton > button:hover { border-color: #818CF8; color: #A5B4FC; }
.stButton > button[kind="primary"] { background: #818CF8; border-color: #818CF8; color: #0B0D12; font-weight: 500; }
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
hr { border-color: #171B24; }
"""

CSS_CLARO = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, button, input { font-family: 'Inter', sans-serif !important; }
.stApp { background: #FBFAF7; }
.block-container { padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1180px; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
section[data-testid="stSidebar"] { background: #F4F2EC; border-right: 1px solid #E7E5E4; }
h1, h2, h3 { font-family: 'Fraunces', Georgia, serif !important; color: #1C1917; letter-spacing: -0.01em; }
h1 { font-weight: 500 !important; font-size: 2.1rem !important; margin-bottom: .1rem; }
h2, h3 { font-weight: 500 !important; font-size: 1.3rem !important; margin-top: 1.8rem; border-bottom: 1px solid #E7E5E4; padding-bottom: 6px; }
.sub { color: #78716C; font-size: .9rem; margin-bottom: 1.6rem; }
.kpi { background: #FFFFFF; border: 1px solid #E7E5E4; border-top: 3px solid #059669; border-radius: 4px; padding: 14px 16px; }
.kpi .l { font-size: .68rem; text-transform: uppercase; letter-spacing: .1em; color: #78716C; font-weight: 600; }
.kpi .v { font-family: 'Fraunces', Georgia, serif; font-size: 1.9rem; font-weight: 500; color: #1C1917; margin-top: 4px; line-height: 1.1; }
.kpi .d { font-size: .76rem; color: #78716C; margin-top: 3px; }
.card { background: #FFFFFF; border: 1px solid #E7E5E4; border-radius: 4px; padding: 16px 18px; margin-bottom: 12px; }
.card h4 { margin: 0 0 6px 0; font-family: 'Fraunces', Georgia, serif; font-size: 1.05rem; font-weight: 500; color: #1C1917; }
.card p { margin: 6px 0 0 0; color: #57534E; font-size: .84rem; line-height: 1.55; }
.pill { display: inline-block; padding: 1px 8px; margin: 0 6px 0 0; border-radius: 2px; font-size: .7rem; color: #047857; background: #ECFDF5; font-weight: 500; }
.banner { background: #F4F2EC; border-radius: 4px; padding: 12px 16px; color: #44403C; font-size: .9rem; margin: .4rem 0 1.2rem 0; }
.banner b { color: #1C1917; }
div[data-testid="stTabs"] button { font-weight: 400; color: #78716C; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #1C1917; }
.stButton > button, .stDownloadButton > button { border-radius: 4px; border: 1px solid #D6D3D1; background: #FFFFFF; color: #1C1917; font-weight: 500; }
.stDownloadButton > button:hover, .stButton > button:hover { border-color: #059669; color: #047857; }
.stButton > button[kind="primary"] { background: #059669; border-color: #059669; color: #fff; }
div[data-testid="stDataFrame"] { border: 1px solid #E7E5E4; border-radius: 4px; overflow: hidden; }
"""

import os
TEMA = os.environ.get("DASH_TEMA", "oscuro").lower()
OSCURO = TEMA != "claro"
CSS_COMUN = """
/* Barra lateral fija: siempre visible, sin botón de ocultar */
section[data-testid="stSidebar"], section[data-testid="stSidebar"][aria-expanded="false"] {
  transform: none !important; margin-left: 0 !important; visibility: visible !important;
  min-width: 270px !important; width: 270px !important; }
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"],
div[data-testid="stSidebarHeader"] button { display: none !important; }
/* Título de la aplicación encima del menú de navegación */
[data-testid="stSidebarNav"]::before {
  content: "◼  Segmentación de clientes"; display: block; padding: 22px 20px 14px 20px;
  font-size: 1.02rem; font-weight: 600; letter-spacing: -0.01em; color: __TITULO__; }
.nota { border-left: 2px solid __ACENTO__; padding: 2px 0 2px 12px; margin: 2px 0 22px 0; font-size: .82rem; line-height: 1.55; opacity: .85; }
.nota b { font-weight: 600; }
[data-testid="stSidebarNav"] a { border-radius: 8px; margin: 1px 10px; }
"""
CSS = (CSS_OSCURO if OSCURO else CSS_CLARO) + CSS_COMUN.replace("__TITULO__", "#F3F4F6" if OSCURO else "#1C1917").replace("__ACENTO__", "#818CF8" if OSCURO else "#059669")



def setup(titulo, icono="◼"):
    st.set_page_config(page_title=f"{titulo} · Segmentación de clientes", page_icon=icono, layout="wide", initial_sidebar_state="expanded")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.caption("Machine Learning no supervisado\nUCI Online Retail")
    if not st.session_state.get(f"_vista_{titulo}"):
        st.session_state[f"_vista_{titulo}"] = True
        log.info(f"Vista abierta: {titulo}")


def header(titulo, sub=""):
    st.markdown(f"# {titulo}")
    if sub:
        st.markdown(f"<div class='sub'>{sub}</div>", unsafe_allow_html=True)


def kpi_row(items):
    for col, (l, v, d) in zip(st.columns(len(items)), items):
        col.markdown(f"<div class='kpi'><div class='l'>{l}</div><div class='v'>{v}</div><div class='d'>{d}</div></div>", unsafe_allow_html=True)


def card(titulo, texto, pills=()):
    p = "".join(f"<span class='pill'>{x}</span>" for x in pills)
    st.markdown(f"<div class='card'><h4>{titulo}</h4>{p}<p>{texto}</p></div>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _csv(ruta, mtime):
    return pd.read_csv(ruta)


@st.cache_data(show_spinner=False)
def _json(ruta, mtime):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def metrica(nombre):
    r = config.METRICS / nombre
    return _json(str(r), r.stat().st_mtime) if nombre.endswith(".json") else _csv(str(r), r.stat().st_mtime)


def clientes():
    r = config.PROCESSED / "clientes_segmentados.csv"
    return _csv(str(r), r.stat().st_mtime)


def requiere_resultados():
    if not (config.METRICS / "resumen.json").exists() or not (config.PROCESSED / "clientes_segmentados.csv").exists():
        st.warning("Aún no hay resultados. Ejecuta `python run_pipeline.py` o usa la página **Bitácora → Re-ejecutar pipeline**.")
        st.stop()


def mapa_color(perfil):
    return {n: PALETA[i % len(PALETA)] for i, n in enumerate(perfil.sort_values("Segmento").Nombre)} | {"Ruido / atípicos": RUIDO}


def estilo(fig, h=360, leyenda=True):
    fig.update_layout(template=PLANTILLA, height=h, margin=dict(l=4, r=4, t=40, b=4), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12, color=TXT),
                      title_font=dict(size=13, color=TXT2), colorway=PALETA, showlegend=leyenda,
                      legend=dict(orientation="h", yanchor="top", y=-0.12, x=0, title_text=""),
                      hoverlabel=dict(bgcolor=HOVER, font_color=TXT2))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, showline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, showline=False)
    return fig


def grafico(fig, h=360, leyenda=True):
    st.plotly_chart(estilo(fig, h, leyenda), use_container_width=True, config={"displayModeBar": False})


import re as _re


def nota(texto):
    """Nota de lectura bajo un gráfico (acepta **negritas**)."""
    html = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    st.markdown(f"<div class='nota'>{html}</div>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _hechos(mtime):
    from src.evaluation import conclusiones
    return conclusiones.hechos()


def hechos():
    return _hechos((config.METRICS / "resumen.json").stat().st_mtime)


def notas():
    from src.evaluation import conclusiones
    return conclusiones.notas(hechos())
