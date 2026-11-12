"""Ejecuta todo el pipeline.  Uso: python run_pipeline.py [--k N] [--sin-pdf]"""
import argparse
from src.pipeline import ejecutar

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=None, help="Forzar número de segmentos en modelos con k")
    ap.add_argument("--sin-pdf", action="store_true")
    a = ap.parse_args()
    r = ejecutar(a.k, not a.sin_pdf)
    print(f"\nListo: {r['n_segmentos']} segmentos con {r['modelo_final']}. Ahora: streamlit run dashboard/app.py")
 