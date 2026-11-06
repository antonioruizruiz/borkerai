import pandas as pd

from app.services.scoring import build_ranking, raw_indicators_from_prices


def _serie_precios(n: int, precio_inicial: float, variacion_diaria_pct: float) -> pd.DataFrame:
    """n sesiones con una variación diaria constante (sube o baja de forma suave)."""
    precios = [precio_inicial * (1 + variacion_diaria_pct) ** i for i in range(n)]
    return pd.DataFrame(
        {
            "close": precios,
            "high": [p * 1.01 for p in precios],
            "low": [p * 0.99 for p in precios],
            "volume": [1_000_000] * n,
        }
    )


def test_sin_historico_suficiente_devuelve_none():
    assert raw_indicators_from_prices(_serie_precios(100, 10, 0.001)) is None


def test_tendencia_alcista_da_momentum_y_tendencia_positivos():
    df = _serie_precios(300, 10, 0.003)  # sube ~0.3% diario
    raw = raw_indicators_from_prices(df)

    assert raw is not None
    assert raw["momentum_raw"] > 0
    assert raw["tendencia_raw"] > 0
    assert raw["volatilidad_raw"] >= 0
    assert raw["distancia_maximo_52_semanas_pct"] <= 0  # el máximo lo marca el propio cierre de hoy (con high*1.01)


def test_tendencia_bajista_da_momentum_negativo():
    df = _serie_precios(300, 50, -0.002)
    raw = raw_indicators_from_prices(df)

    assert raw is not None
    assert raw["momentum_raw"] < 0
    assert raw["tendencia_raw"] < 0


def test_build_ranking_ordena_por_percentil_y_calcula_fuerza_sector():
    subida = raw_indicators_from_prices(_serie_precios(300, 10, 0.004))
    bajada = raw_indicators_from_prices(_serie_precios(300, 10, -0.002))
    plana = raw_indicators_from_prices(_serie_precios(300, 10, 0.0001))

    filas = [
        {"ticker": "SUBE.MC", "name": "Sube", "sector": "A", **subida},
        {"ticker": "BAJA.MC", "name": "Baja", "sector": "B", **bajada},
        {"ticker": "PLANA.MC", "name": "Plana", "sector": "A", **plana},
    ]

    ranking = build_ranking(filas)
    por_ticker = {fila["ticker"]: fila for fila in ranking}

    assert por_ticker["SUBE.MC"]["momentum"] == 100.0
    assert por_ticker["BAJA.MC"]["momentum"] == _valor_minimo(ranking, "momentum")
    assert por_ticker["SUBE.MC"]["score_global"] > por_ticker["BAJA.MC"]["score_global"]
    # Todos los factores son percentiles 0-100
    for fila in ranking:
        for factor in ["momentum", "tendencia", "estabilidad", "fuerza_sector", "score_global"]:
            assert fila[factor] is not None
            assert 0 <= fila[factor] <= 100


def test_build_ranking_empresa_sin_historico_queda_con_factores_none_salvo_sector():
    subida = raw_indicators_from_prices(_serie_precios(300, 10, 0.004))
    sin_datos = {
        "momentum_raw": None,
        "tendencia_raw": None,
        "volatilidad_raw": None,
        "distancia_maximo_52_semanas_pct": None,
        "volumen_relativo": None,
    }

    filas = [
        {"ticker": "CONDATOS.MC", "name": "Con datos", "sector": "A", **subida},
        {"ticker": "NUEVA.MC", "name": "Recién salida a bolsa", "sector": "A", **sin_datos},
    ]

    ranking = build_ranking(filas)
    por_ticker = {fila["ticker"]: fila for fila in ranking}

    assert por_ticker["NUEVA.MC"]["momentum"] is None
    assert por_ticker["NUEVA.MC"]["score_global"] is None
    # La fuerza del sector es del sector entero, así que sí puede calcularse
    assert por_ticker["NUEVA.MC"]["fuerza_sector"] is not None


def _valor_minimo(ranking, campo):
    return min(fila[campo] for fila in ranking)
