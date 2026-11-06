"""Cálculos de la página Cartera (Fase 7): valor actual, ganancia/pérdida de cada
posición, y un aviso sencillo según el tipo de posición (corto plazo, largo plazo,
dividendos) — una "revisión diaria" básica, no una recomendación de la IA.
"""
from __future__ import annotations

UMBRAL_PERDIDA_CORTO_PLAZO_PCT = -5.0
UMBRAL_GANANCIA_CORTO_PLAZO_PCT = 15.0
UMBRAL_PERDIDA_LARGO_PLAZO_PCT = -20.0


def calcular_posicion(precio_compra: float, cantidad: int, precio_actual: float | None) -> dict:
    if precio_actual is None:
        return {
            "precio_actual": None,
            "valor_actual_euros": None,
            "ganancia_perdida_euros": None,
            "ganancia_perdida_pct": None,
        }

    valor_compra = precio_compra * cantidad
    valor_actual = precio_actual * cantidad
    ganancia_perdida_euros = valor_actual - valor_compra
    ganancia_perdida_pct = (ganancia_perdida_euros / valor_compra * 100) if valor_compra else None

    return {
        "precio_actual": round(precio_actual, 2),
        "valor_actual_euros": round(valor_actual, 2),
        "ganancia_perdida_euros": round(ganancia_perdida_euros, 2),
        "ganancia_perdida_pct": round(ganancia_perdida_pct, 2) if ganancia_perdida_pct is not None else None,
    }


def evaluar_aviso(tipo: str, ganancia_perdida_pct: float | None, fecha_estimada_proximo_dividendo=None) -> str | None:
    """Un aviso simple y explicable, distinto según para qué se compró la posición."""
    if tipo == "dividendos":
        if fecha_estimada_proximo_dividendo is not None:
            return f"Próximo dividendo estimado el {fecha_estimada_proximo_dividendo.strftime('%d/%m/%Y')}."
        return None

    if ganancia_perdida_pct is None:
        return None

    if tipo == "corto_plazo":
        if ganancia_perdida_pct <= UMBRAL_PERDIDA_CORTO_PLAZO_PCT:
            return f"Revisar: pérdida de {ganancia_perdida_pct:.1f}% en una posición a corto plazo."
        if ganancia_perdida_pct >= UMBRAL_GANANCIA_CORTO_PLAZO_PCT:
            return f"En ganancia de {ganancia_perdida_pct:.1f}%: valora asegurar beneficios."
        return None

    if tipo == "largo_plazo":
        if ganancia_perdida_pct <= UMBRAL_PERDIDA_LARGO_PLAZO_PCT:
            return f"Revisar: pérdida de {ganancia_perdida_pct:.1f}% en una posición a largo plazo."
        return None

    return None
