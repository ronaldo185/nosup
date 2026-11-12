@echo off
if not exist .venv ( python -m venv .venv & call .venv\Scripts\activate & pip install -r requirements.txt ) else ( call .venv\Scripts\activate )
if not exist results\metrics\resumen.json python run_pipeline.py
streamlit run dashboard/app.py
