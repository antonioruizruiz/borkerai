"""Combina los 4 universos de empresas en un único listado para sembrar `Company`,
asignando el campo `indice` según el grupo de origen (None para `sueltas`).

Orden de combinación IMPORTANTE: si un ticker aparece en más de un grupo (pasa entre
Dow Jones y Nasdaq-100: p. ej. AAPL, MSFT, NVDA, AMZN, CSCO, HON, AMGN), se queda con
la asignación del ÚLTIMO grupo en el que aparece. Por eso NASDAQ100 va después de
DOWJONES: así esas empresas quedan como "NASDAQ100" (es donde cotizan realmente),
como se decidió explícitamente para esta app.
"""
from app.data.dowjones import DOWJONES
from app.data.ibex35 import IBEX35
from app.data.nasdaq100 import NASDAQ100
from app.data.sueltas import SUELTAS

_GRUPOS: list[tuple[str | None, list[dict]]] = [
    ("IBEX35", IBEX35),
    ("DOWJONES", DOWJONES),
    ("NASDAQ100", NASDAQ100),
    (None, SUELTAS),
]


def universo_completo() -> list[dict]:
    """Una entrada por ticker (dict con ticker/name/sector/moneda/indice)."""
    por_ticker: dict[str, dict] = {}
    for indice, grupo in _GRUPOS:
        for empresa in grupo:
            por_ticker[empresa["ticker"]] = {**empresa, "indice": indice}
    return list(por_ticker.values())
