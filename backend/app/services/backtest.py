"""Backtest de las reglas de entrada (Fase 4) sobre el histórico de precios (Fase 5).

Para cada señal que se habría activado en el pasado, simula qué habría pasado después
(toca el objetivo, toca el stop, o se acaba el plazo sin tocar ninguno), descontando
siempre comisiones y deslizamiento, y guarda el seguimiento a D+1/D+5/D+10/D+20. Con
eso se construye la página Fiabilidad: mide, con datos reales ya ocurridos, si las
reglas funcionan y cómo se comparan con haberse quedado quieto en el IBEX 35.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import pandas_ta as ta

MINIMO_SESIONES_REQUERIDO = 273  # igual que en scoring.py: hace falta ~13 meses de histórico
UMBRAL_VOLUMEN_RUPTURA = 1.5
MARGEN_PULLBACK_SMA50_PCT = 2.0
RATIO_BENEFICIO_RIESGO_OBJETIVO = 2.0
PLAZO_SESIONES_RUPTURA = 20  # ~4 semanas ("corto plazo", igual que en recommendations.py)
PLAZO_SESIONES_PULLBACK = 60  # ~3 meses ("medio plazo")
HORIZONTES_SEGUIMIENTO = [1, 5, 10, 20]


def _calcular_niveles(df: pd.DataFrame) -> pd.DataFrame:
    """Indicadores de cada sesión (vectorizado) y si ese día se cumple cada regla de entrada."""
    close, volume = df["close"], df["volume"]

    sma50 = ta.sma(close, length=50)
    sma200 = ta.sma(close, length=200)
    maximo_252_previo = df["high"].shift(1).rolling(252).max()
    volumen_medio_20 = volume.rolling(20).mean()
    minimo_10 = df["low"].rolling(10).min()

    ruptura = (close > maximo_252_previo) & (volume >= UMBRAL_VOLUMEN_RUPTURA * volumen_medio_20)

    tendencia_alcista = (sma50 > sma200) & (close > sma200)
    distancia_sma50_pct = (close / sma50 - 1) * 100
    pullback = tendencia_alcista & (distancia_sma50_pct >= 0) & (distancia_sma50_pct <= MARGEN_PULLBACK_SMA50_PCT)

    return pd.DataFrame(
        {
            "ruptura": ruptura.fillna(False),
            "pullback": (pullback & ~ruptura).fillna(False),  # si hay ruptura ese día, prioriza esa regla
            "stop_ruptura": minimo_10,
            "stop_pullback": pd.concat([sma200, minimo_10], axis=1).min(axis=1),
        }
    )


def _coste_operacion(precio: float, acciones: int, ajustes) -> float:
    return max(ajustes.comision_minima, precio * acciones * ajustes.comision_pct / 100) + (
        precio * acciones * ajustes.deslizamiento_pct / 100
    )


def _seguimiento(close: pd.Series, idx_entrada: int, entrada: float) -> dict:
    seguimiento = {}
    for horizonte in HORIZONTES_SEGUIMIENTO:
        idx_objetivo = idx_entrada + horizonte
        clave = f"seguimiento_d{horizonte}_pct"
        seguimiento[clave] = (
            round((close.iloc[idx_objetivo] / entrada - 1) * 100, 2) if idx_objetivo < len(close) else None
        )
    return seguimiento


def simular_operaciones(df: pd.DataFrame, ajustes) -> list[dict]:
    """`df`: histórico (date/close/high/low/volume) de UNA empresa, ordenado por fecha ascendente.

    Una operación por cada señal histórica, sin solapar: mientras una sigue "abierta" en
    la simulación, no se abren nuevas en la misma empresa (igual que haría una persona).
    """
    if len(df) < MINIMO_SESIONES_REQUERIDO:
        return []

    niveles = _calcular_niveles(df)
    fechas = df["date"].reset_index(drop=True)
    close = df["close"].reset_index(drop=True)
    high = df["high"].reset_index(drop=True)
    low = df["low"].reset_index(drop=True)
    niveles = niveles.reset_index(drop=True)

    operaciones: list[dict] = []
    idx = MINIMO_SESIONES_REQUERIDO
    while idx < len(df):
        if niveles["ruptura"].iloc[idx]:
            regla, stop, plazo = "Ruptura de máximos con volumen", niveles["stop_ruptura"].iloc[idx], PLAZO_SESIONES_RUPTURA
        elif niveles["pullback"].iloc[idx]:
            regla, stop, plazo = "Retroceso en tendencia alcista", niveles["stop_pullback"].iloc[idx], PLAZO_SESIONES_PULLBACK
        else:
            idx += 1
            continue

        entrada = close.iloc[idx]
        if pd.isna(stop) or stop >= entrada:
            idx += 1
            continue

        objetivo = entrada + RATIO_BENEFICIO_RIESGO_OBJETIVO * (entrada - stop)
        seguimiento = _seguimiento(close, idx, entrada)

        limite = min(idx + plazo, len(df) - 1)
        idx_salida, motivo_salida, precio_salida = limite, "tiempo", close.iloc[limite]
        for j in range(idx + 1, limite + 1):
            if low.iloc[j] <= stop:
                idx_salida, motivo_salida, precio_salida = j, "stop", stop
                break
            if high.iloc[j] >= objetivo:
                idx_salida, motivo_salida, precio_salida = j, "objetivo", objetivo
                break

        riesgo_euros_maximo = ajustes.capital_total * ajustes.riesgo_pct_operacion / 100
        acciones = int(riesgo_euros_maximo // (entrada - stop))

        if acciones > 0:
            coste_entrada = _coste_operacion(entrada, acciones, ajustes)
            coste_salida = _coste_operacion(precio_salida, acciones, ajustes)
            beneficio_neto = (precio_salida - entrada) * acciones - coste_entrada - coste_salida
            riesgo_bruto_euros = (entrada - stop) * acciones

            operaciones.append(
                {
                    "regla": regla,
                    "fecha_entrada": fechas.iloc[idx],
                    "fecha_salida": fechas.iloc[idx_salida],
                    "dias_en_posicion": idx_salida - idx,
                    "entrada": round(entrada, 2),
                    "stop": round(stop, 2),
                    "objetivo": round(objetivo, 2),
                    "precio_salida": round(precio_salida, 2),
                    "motivo_salida": motivo_salida,
                    "acciones": acciones,
                    "beneficio_neto_euros": round(beneficio_neto, 2),
                    "retorno_pct": round((precio_salida / entrada - 1) * 100, 2),
                    "beneficio_riesgo_neto": (
                        round(beneficio_neto / riesgo_bruto_euros, 2) if riesgo_bruto_euros > 0 else None
                    ),
                    "acierto": bool(beneficio_neto > 0),
                    **seguimiento,
                }
            )

        idx = idx_salida + 1

    return operaciones


def _media(valores: list[float | None]) -> float | None:
    limpios = [v for v in valores if v is not None]
    return round(sum(limpios) / len(limpios), 2) if limpios else None


def resumen_por_regla(operaciones: list[dict]) -> dict:
    if not operaciones:
        return {
            "n_operaciones": 0,
            "tasa_acierto_pct": None,
            "retorno_medio_pct": None,
            "beneficio_riesgo_neto_medio": None,
        }
    return {
        "n_operaciones": len(operaciones),
        "tasa_acierto_pct": round(100 * sum(o["acierto"] for o in operaciones) / len(operaciones), 1),
        "retorno_medio_pct": _media([o["retorno_pct"] for o in operaciones]),
        "beneficio_riesgo_neto_medio": _media([o["beneficio_riesgo_neto"] for o in operaciones]),
    }


def resumen_fiabilidad(operaciones: list[dict]) -> dict:
    """Agregados globales, por regla, y seguimiento medio D+1/D+5/D+10/D+20 de TODAS las
    operaciones simuladas (de todas las empresas)."""
    por_regla = {
        regla: resumen_por_regla([o for o in operaciones if o["regla"] == regla])
        for regla in sorted({o["regla"] for o in operaciones})
    }

    seguimiento_medio = {
        f"d{h}_pct": _media([o[f"seguimiento_d{h}_pct"] for o in operaciones]) for h in HORIZONTES_SEGUIMIENTO
    }

    return {
        "resumen_global": resumen_por_regla(operaciones),
        "por_regla": por_regla,
        "seguimiento_medio": seguimiento_medio,
    }


def comparacion_indice(index_df: pd.DataFrame, periodo_inicio: date, periodo_fin: date) -> dict | None:
    """Rentabilidad de haberse quedado quieto en el IBEX 35 (comprar y mantener, sin hacer
    nada) durante el mismo periodo que cubre el backtest. None si no hay histórico del índice."""
    if index_df.empty:
        return None

    en_periodo = index_df[(index_df["date"] >= periodo_inicio) & (index_df["date"] <= periodo_fin)]
    if len(en_periodo) < 2:
        return None

    precio_inicio = en_periodo["close"].iloc[0]
    precio_fin = en_periodo["close"].iloc[-1]
    fecha_inicio = en_periodo["date"].iloc[0]
    fecha_fin = en_periodo["date"].iloc[-1]

    retorno_total_pct = (precio_fin / precio_inicio - 1) * 100
    años = (fecha_fin - fecha_inicio).days / 365.25
    retorno_anualizado_pct = ((1 + retorno_total_pct / 100) ** (1 / años) - 1) * 100 if años > 0 else None

    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "retorno_total_pct": round(retorno_total_pct, 2),
        "retorno_anualizado_pct": round(retorno_anualizado_pct, 2) if retorno_anualizado_pct is not None else None,
    }
