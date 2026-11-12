#!/usr/bin/env bash
# Diseño alternativo: tema claro editorial
. .venv/bin/activate 2>/dev/null || true
export DASH_TEMA=claro STREAMLIT_THEME_BASE=light STREAMLIT_THEME_PRIMARY_COLOR="#059669" \
  STREAMLIT_THEME_BACKGROUND_COLOR="#FBFAF7" STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR="#F4F2EC" STREAMLIT_THEME_TEXT_COLOR="#1C1917"
streamlit run dashboard/app.py --server.port 8502
