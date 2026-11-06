"""Generación del plan de recomendaciones (Fase 4): reglas de entrada, plan de
orden límite / stop / objetivo / plazo, tamaño de posición según capital y riesgo,
y clasificación de riesgo. Es un paso puramente mecánico y explicable a partir de
indicadores técnicos: la revisión con la IA de Claude (que puede matizar o frenar,
nunca inventar compras) es la Fase 6, todavía no entra aquí.
"""
from __future__ import annotations

import pandas as pd

from app.services.scoring import raw_indicators_from_prices

UMBRAL_VOLUMEN_RUPTURA = 1.5  # volumen de hoy >= 1.5x la media de las últimas 20 sesiones
MARGEN_VIGILANCIA_RUPTURA_PCT = 2.0  # a menos de un 2% del máximo de 52 semanas => "en vigilancia"
MARGEN_PULLBACK_SMA50_PCT = 2.0  # precio a menos de un 2% de su media de 50 sesiones
RATIO_BENEFICIO_RIESGO_OBJETIVO = 2.0  # objetivo = entrada + 2 x riesgo por acción (antes de costes)


def _clasificar_riesgo(estabilidad: float | None) -> str:
    """A partir del factor 0-100 de Estabilidad del Ranking (Fase 3)."""
    if estabilidad is None:
        return "desconocido"
    if estabilidad >= 66:
        return "bajo"
    if estabilidad >= 33:
        return "medio"
    return "alto"


def _evaluar_ruptura(df: pd.DataFrame, raw: dict) -> dict | None:
    """Regla "ruptura de máximos con volumen": nuevo máximo de 52 semanas acompañado
    de un volumen muy por encima de lo habitual (confirma que hay interés comprador real)."""
    maximo_previo = df["high"].iloc[:-1].tail(252).max()
    precio_actual = raw["precio_actual"]
    volumen_actual = raw["volumen_actual"]
    volumen_medio_20d = raw["volumen_medio_20d"]

    distancia_pct = (precio_actual / maximo_previo - 1) * 100
    volumen_veces_la_media = (volumen_actual / volumen_medio_20d) if volumen_medio_20d else 0

    if precio_actual > maximo_previo and volumen_veces_la_media >= UMBRAL_VOLUMEN_RUPTURA:
        return {
            "regla": "Ruptura de máximos con volumen",
            "motivo": (
                f"Ha superado su máximo de las últimas 52 semanas ({maximo_previo:.2f} €) con un volumen "
                f"{volumen_veces_la_media:.1f} veces el habitual de las últimas 20 sesiones."
            ),
            "entrada": precio_actual,
            "stop": raw["minimo_10_sesiones"],
            "plazo": "corto plazo (2-4 semanas)",
        }
    if -MARGEN_VIGILANCIA_RUPTURA_PCT <= distancia_pct < 0:
        return {
            "vigilancia": True,
            "regla": "Cerca de romper máximos",
            "motivo": f"Cotiza a un {abs(distancia_pct):.1f}% de su máximo de 52 semanas ({maximo_previo:.2f} €).",
        }
    return None


def _evaluar_pullback(raw: dict) -> dict | None:
    """Regla "retroceso en tendencia": tendencia alcista establecida (media de 50
    por encima de la de 200) con el precio volviendo cerca de su media de 50 sesiones,
    un punto de entrada clásico para sumarse a una tendencia ya en marcha."""
    sma50 = raw["sma50"]
    sma200 = raw["sma200"]
    precio_actual = raw["precio_actual"]
    if not sma50 or not sma200 or not (sma50 > sma200 and precio_actual > sma200):
        return None

    distancia_sma50_pct = (precio_actual / sma50 - 1) * 100

    if 0 <= distancia_sma50_pct <= MARGEN_PULLBACK_SMA50_PCT:
        return {
            "regla": "Retroceso en tendencia alcista",
            "motivo": (
                f"Tendencia alcista (media de 50 sesiones por encima de la de 200) con el precio cerca de "
                f"su media de 50 sesiones ({sma50:.2f} €): posible punto de entrada en el retroceso."
            ),
            "entrada": precio_actual,
            "stop": min(sma200, raw["minimo_10_sesiones"]),
            "plazo": "medio plazo (1-3 meses)",
        }
    if -MARGEN_PULLBACK_SMA50_PCT <= distancia_sma50_pct < 0:
        return {
            "vigilancia": True,
            "regla": "Posible retroceso en tendencia alcista",
            "motivo": (
                f"Tendencia alcista, con el precio a un {abs(distancia_sma50_pct):.1f}% por debajo de su "
                "media de 50 sesiones: vigilar si rebota ahí."
            ),
        }
    return None


def _plan_con_costes(entrada: float, stop: float, objetivo: float, acciones: int, ajustes) -> dict | None:
    """Beneficio/riesgo neto de comisiones y deslizamiento, ya con el número de
    acciones fijado. None si no hay forma de abrir una posición viable."""
    if acciones <= 0:
        return None

    def coste_operacion(precio: float) -> float:
        return max(ajustes.comision_minima, precio * acciones * ajustes.comision_pct / 100) + (
            precio * acciones * ajustes.deslizamiento_pct / 100
        )

    coste_compra = coste_operacion(entrada)
    beneficio_neto = (objetivo - entrada) * acciones - coste_compra - coste_operacion(objetivo)
    riesgo_neto = (entrada - stop) * acciones + coste_compra + coste_operacion(stop)

    return {
        "acciones": acciones,
        "beneficio_riesgo_neto": round(beneficio_neto / riesgo_neto, 2) if riesgo_neto > 0 else None,
    }


def generar_recomendacion(df: pd.DataFrame, estabilidad: float | None, ajustes) -> dict | None:
    """`df`: histórico (close/high/low/volume) de UNA empresa, ordenado por fecha ascendente.
    `ajustes`: TradingSettings (capital_total, riesgo_pct_operacion, comision_pct, comision_minima,
    deslizamiento_pct).

    Devuelve None si no hay histórico suficiente o no se activa/aproxima ninguna regla.
    Si vuelve con `"vigilancia": True`, es una señal que se está formando, sin plan de
    compra todavía. Si no, trae el plan completo (entrada/stop/objetivo/plazo/acciones/riesgo).
    """
    raw = raw_indicators_from_prices(df)
    if raw is None:
        return None

    señal = _evaluar_ruptura(df, raw) or _evaluar_pullback(raw)
    if señal is None:
        return None
    if señal.get("vigilancia"):
        return señal

    entrada = señal["entrada"]
    stop = señal["stop"]
    if stop is None or stop >= entrada:
        return None

    riesgo_por_accion = entrada - stop
    objetivo = entrada + RATIO_BENEFICIO_RIESGO_OBJETIVO * riesgo_por_accion

    riesgo_euros_maximo = ajustes.capital_total * ajustes.riesgo_pct_operacion / 100
    acciones = int(riesgo_euros_maximo // riesgo_por_accion)

    plan = _plan_con_costes(entrada, stop, objetivo, acciones, ajustes)
    if plan is None:
        return None

    return {
        **señal,
        "entrada": round(entrada, 2),
        "stop": round(stop, 2),
        "objetivo": round(objetivo, 2),
        "riesgo": _clasificar_riesgo(estabilidad),
        **plan,
    }
