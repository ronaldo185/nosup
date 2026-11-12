"""Bitácora: log en archivo + historial de ejecuciones en JSON."""
import json, logging, datetime as dt
from src import config

LOG_FILE = config.LOGS / "bitacora.log"
RUNS_FILE = config.LOGS / "ejecuciones.json"


def get_logger(nombre="sistema"):
    config.LOGS.mkdir(parents=True, exist_ok=True)
    lg = logging.getLogger(nombre)
    if not lg.handlers:
        lg.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)-10s | %(message)s", "%Y-%m-%d %H:%M:%S")
        for h in (logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()):
            h.setFormatter(fmt); lg.addHandler(h)
    return lg


def guardar_ejecucion(registro: dict):
    hist = leer_ejecuciones()
    hist.append(registro)
    RUNS_FILE.write_text(json.dumps(hist, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def leer_ejecuciones():
    return json.loads(RUNS_FILE.read_text(encoding="utf-8")) if RUNS_FILE.exists() else []


def leer_log(max_lineas=2000):
    if not LOG_FILE.exists():
        return []
    return LOG_FILE.read_text(encoding="utf-8").splitlines()[-max_lineas:]
