"""Indicadores técnicos y factores 0-100 para el Ranking (Fase 3).

Dos pasos:
1. `raw_indicators_from_prices`: a partir del histórico de UNA empresa, calcula
   valores "en crudo" (medias, momentum, volatilidad...).
2. `build_ranking`: con los valores en crudo de TODAS las empresas, convierte
   cada indicador en un factor 0-100 por *percentil frente al resto del IBEX 35*
   (no es una nota absoluta: 80 significa "mejor que el 80% de sus compañeras hoy").

De momento solo se usan precio y volumen. "Calidad" y "valoración" (que requieren
datos fundamentales de balance/resultados) se añadirán en una fase posterior.
"""
from __future__ import annotations

import math

import pandas as pd
import pandas_ta as ta

SESIONES_MOMENTUM_LARGO = 252  # ~12 meses de sesiones bursátiles
SESIONES_MOMENTUM_CORTO = 21  # ~1 mes (se excluye del momentum 12-1)
SESIONES_VOLATILIDAD = 60  # ~3 meses
SESIONES_VOLUMEN_RELATIVO = 20  # ~1 mes
SESIONES_MAXIMO_52_SEMANAS = 252

MINIMO_SESIONES_REQUERIDO = SESIONES_MOMENTUM_LARGO + SESIONES_MOMENTUM_CORTO


def raw_indicators_from_prices(df: pd.DataFrame) -> dict | None:
    """`df` con columnas close, high, low, volume, ordenado por fecha ascendente.

    Devuelve None si no hay histórico suficiente (menos de ~13 meses de sesiones).
    """
    if len(df) < MINIMO_SESIONES_REQUERIDO:
        return None

    close = df["close"]
    high = df["high"]
    volume = df["volume"]

    sma50 = ta.sma(close, length=50).iloc[-1]
    sma200 = ta.sma(close, length=200).iloc[-1]
    precio_actual = close.iloc[-1]

    momentum_12_1 = (close.iloc[-SESIONES_MOMENTUM_CORTO] / close.iloc[-SESIONES_MOMENTUM_LARGO]) - 1

    retornos_diarios = close.pct_change()
    volatilidad_anualizada = ta.stdev(retornos_diarios, length=SESIONES_VOLATILIDAD).iloc[-1] * (252**0.5)

    maximo_52_semanas = high.tail(SESIONES_MAXIMO_52_SEMANAS).max()
    distancia_al_maximo_pct = (precio_actual / maximo_52_semanas) - 1  # 0 = en máximos, negativo = por debajo

    volumen_medio_20d = volume.tail(SESIONES_VOLUMEN_RELATIVO).mean()
    volumen_relativo = (volume.iloc[-1] / volumen_medio_20d) if volumen_medio_20d else None

    tendencia_raw = None
    if sma50 and sma200:
        tendencia_raw = 0.5 * ((precio_actual / sma50) - 1) + 0.5 * ((precio_actual / sma200) - 1)

    minimo_10_sesiones = df["low"].tail(10).min()

    return {
        "momentum_raw": momentum_12_1,
        "tendencia_raw": tendencia_raw,
        "volatilidad_raw": volatilidad_anualizada,
        "distancia_maximo_52_semanas_pct": round(distancia_al_maximo_pct * 100, 2),
        "volumen_relativo": round(volumen_relativo, 2) if volumen_relativo is not None else None,
        # Niveles en crudo (no son factores 0-100): los usa el servicio de
        # recomendaciones (Fase 4) para fijar entrada/stop/objetivo.
        "precio_actual": precio_actual,
        "sma50": sma50 if pd.notna(sma50) else None,
        "sma200": sma200 if pd.notna(sma200) else None,
        "maximo_52_semanas": maximo_52_semanas,
        "minimo_10_sesiones": minimo_10_sesiones,
        "volumen_actual": volume.iloc[-1],
        "volumen_medio_20d": volumen_medio_20d,
    }


def _percentil_0_100(serie: pd.Series, ascendente: bool = True) -> pd.Series:
    """Percentil 0-100 de cada valor frente al resto de la serie.

    `ascendente=False` cuando un valor más bajo es "mejor" (p. ej. volatilidad),
    así el percentil más alto corresponde al valor más favorable.
    """
    return serie.rank(pct=True, ascending=ascendente) * 100


def build_ranking(filas: list[dict]) -> list[dict]:
    """`filas`: una por empresa, con ticker/name/sector + los *_raw de arriba (o None).

    Devuelve las mismas empresas con los factores 0-100 añadidos. Las empresas sin
    histórico suficiente (raws en None) se devuelven con los factores en None.
    """
    df = pd.DataFrame(filas).set_index("ticker")

    con_datos = df.dropna(subset=["momentum_raw", "tendencia_raw", "volatilidad_raw"])

    df["momentum"] = _percentil_0_100(con_datos["momentum_raw"]).reindex(df.index)
    df["tendencia"] = _percentil_0_100(con_datos["tendencia_raw"]).reindex(df.index)
    df["estabilidad"] = _percentil_0_100(con_datos["volatilidad_raw"], ascendente=False).reindex(df.index)

    momentum_medio_sector = con_datos.groupby("sector")["momentum_raw"].mean()
    percentil_sector = _percentil_0_100(momentum_medio_sector)
    df["fuerza_sector"] = df["sector"].map(percentil_sector)

    factores = ["momentum", "tendencia", "estabilidad", "fuerza_sector"]
    df["score_global"] = df[factores].mean(axis=1, skipna=False)

    for col in [*factores, "score_global"]:
        df[col] = df[col].round(1)

    registros = df.reset_index().to_dict(orient="records")
    # NaN (de columnas numéricas de pandas) -> None de Python, para que se note la
    # ausencia de dato en vez de un número inválido.
    return [
        {clave: (None if isinstance(valor, float) and math.isnan(valor) else valor) for clave, valor in fila.items()}
        for fila in registros
    ]
