#!/usr/bin/env bash
set -e
[ -d .venv ] || { python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt; }
. .venv/bin/activate
[ -f results/metrics/resumen.json ] || python run_pipeline.py
streamlit run dashboard/app.py
