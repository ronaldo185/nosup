"""Configuración central del proyecto (rutas y parámetros)."""
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW, INTERIM, PROCESSED = ROOT / "data/raw", ROOT / "data/interim", ROOT / "data/processed"
RESULTS = ROOT / "results"
FIGURES, METRICS, MODELS, LOGS = (RESULTS / x for x in ("figures", "metrics", "models", "logs"))
DOCS = ROOT / "docs"

SEED = 42
# Variables usadas para agrupar (se transforman con log1p + estandarización)
FEATURES = ["Recency", "Frequency", "Monetary", "AvgTicket", "UniqueProducts"]
K_RANGE = range(2, 11)          # rango explorado
K_MIN_NEGOCIO, K_MAX_NEGOCIO = 4, 8   # k interpretable para marketing (k=2-3 es demasiado grueso)
MAX_RUIDO_PCT = 10.0            # ruido máximo aceptable para elegir modelo final
NO_PRODUCTO = ["POST", "D", "DOT", "M", "m", "BANK CHARGES", "S", "AMAZONFEE", "B", "CRUK", "PADS", "C2"]

PALETA = ["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#F43F5E", "#8B5CF6", "#14B8A6", "#64748B"]
