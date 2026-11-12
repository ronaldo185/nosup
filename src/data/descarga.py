"""Descarga opcional del dataset desde UCI (requiere internet y `pip install ucimlrepo`)."""
from src import config


def descargar():
    from ucimlrepo import fetch_ucirepo  # id 352 = Online Retail
    d = fetch_ucirepo(id=352)
    df = d.data.original
    config.RAW.mkdir(parents=True, exist_ok=True)
    df.to_excel(config.RAW / "Online Retail.xlsx", index=False)
    return df


if __name__ == "__main__":
    descargar()
