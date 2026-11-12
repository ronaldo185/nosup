@echo off
if exist .venv\Scripts\activate call .venv\Scripts\activate
set DASH_TEMA=claro
set STREAMLIT_THEME_BASE=light
set STREAMLIT_THEME_PRIMARY_COLOR=#059669
set STREAMLIT_THEME_BACKGROUND_COLOR=#FBFAF7
set STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR=#F4F2EC
set STREAMLIT_THEME_TEXT_COLOR=#1C1917
streamlit run dashboard/app.py --server.port 8502
