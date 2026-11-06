"""Resumen de dividendos de una empresa (Fase 7, página Dividendos): rentabilidad
sobre el último año, historial reciente y una fecha estimada del próximo pago.

La fecha "estimada" es solo eso: una estimación a partir del intervalo medio entre
los últimos pagos. No viene confirmada por la empresa, así que nunca se presenta
como un hecho seguro.
"""
from __future__ import annotations

from datetime import date, timedelta

DIAS_ULTIMO_ANIO = 365
MAXIMO_PAGOS_PARA_INTERVALO = 4
MAXIMO_HISTORIAL = 8


def resumen_dividendos(dividendos: list, last_price: float | None) -> dict:
    """`dividendos`: objetos con `.date` y `.amount`, ya ordenados de más reciente a más antiguo."""
    if not dividendos:
        return {
            "rentabilidad_pct": None,
            "total_ultimo_anio_euros": None,
            "fecha_ultimo": None,
            "importe_ultimo": None,
            "fecha_estimada_proximo": None,
            "historial": [],
        }

    hace_un_anio = date.today() - timedelta(days=DIAS_ULTIMO_ANIO)
    total_ultimo_anio = sum(d.amount for d in dividendos if d.date >= hace_un_anio)
    rentabilidad_pct = (total_ultimo_anio / last_price * 100) if last_price else None

    ultimo = dividendos[0]
    fecha_estimada_proximo = None
    recientes = dividendos[:MAXIMO_PAGOS_PARA_INTERVALO]
    if len(recientes) >= 2:
        intervalos = [(recientes[i].date - recientes[i + 1].date).days for i in range(len(recientes) - 1)]
        intervalo_medio = sum(intervalos) / len(intervalos)
        fecha_estimada_proximo = ultimo.date + timedelta(days=round(intervalo_medio))

    return {
        "rentabilidad_pct": round(rentabilidad_pct, 2) if rentabilidad_pct is not None else None,
        "total_ultimo_anio_euros": round(total_ultimo_anio, 4),
        "fecha_ultimo": ultimo.date,
        "importe_ultimo": ultimo.amount,
        "fecha_estimada_proximo": fecha_estimada_proximo,
        "historial": [{"date": d.date, "amount": d.amount} for d in dividendos[:MAXIMO_HISTORIAL]],
    }
