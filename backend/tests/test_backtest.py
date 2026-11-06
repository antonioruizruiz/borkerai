from datetime import date, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest

from app.services.backtest import comparacion_indice, resumen_fiabilidad, simular_operaciones

AJUSTES = SimpleNamespace(
    capital_total=10_000.0,
    riesgo_pct_operacion=1.0,
    comision_pct=0.1,
    comision_minima=2.0,
    deslizamiento_pct=0.05,
)


def _con_fechas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = [date(2015, 1, 1) + timedelta(days=i) for i in range(len(df))]
    return df


def _df_ruptura_con_cola(filas_cola: list[dict], n_base: int = 279) -> pd.DataFrame:
    """279 sesiones planas a 50 €, una sesión de ruptura (salto de precio + volumen) y
    después las sesiones de `filas_cola` (lo que pasa tras la señal)."""
    precios_base = [50.0] * n_base
    senal = precios_base[-1] * 1.05
    base = pd.DataFrame(
        {
            "close": precios_base + [senal],
            "high": [p * 1.003 for p in precios_base] + [senal * 1.001],
            "low": [p * 0.997 for p in precios_base + [senal]],
            "volume": [1_000_000] * n_base + [3_000_000],
        }
    )
    cola = pd.DataFrame(filas_cola)
    return _con_fechas(pd.concat([base, cola], ignore_index=True))


def test_sin_historico_suficiente_no_hay_operaciones():
    df = _con_fechas(pd.DataFrame({"close": [50.0] * 100, "high": [50.3] * 100, "low": [49.7] * 100, "volume": [1_000_000] * 100}))
    assert simular_operaciones(df, AJUSTES) == []


def test_ruptura_que_toca_objetivo():
    # entrada=52.5, stop=49.85, objetivo=57.8 (comprobado por separado)
    cola = [
        {"close": 54, "high": 54.2, "low": 53.8, "volume": 1_000_000},
        {"close": 56, "high": 56.2, "low": 55.8, "volume": 1_000_000},
        {"close": 58, "high": 58.2, "low": 57.6, "volume": 1_000_000},  # toca objetivo (57.8) aquí
    ]
    df = _df_ruptura_con_cola(cola)
    operaciones = simular_operaciones(df, AJUSTES)

    assert len(operaciones) == 1
    op = operaciones[0]
    assert op["regla"] == "Ruptura de máximos con volumen"
    assert op["entrada"] == 52.5
    assert op["stop"] == 49.85
    assert op["objetivo"] == 57.8
    assert op["motivo_salida"] == "objetivo"
    assert op["precio_salida"] == 57.8
    assert op["dias_en_posicion"] == 3
    assert op["acierto"] is True
    assert op["beneficio_neto_euros"] > 0
    # Algo por debajo de 2.0 (el objetivo bruto): los costes recortan un poco el beneficio neto.
    assert 1.8 < op["beneficio_riesgo_neto"] <= 2.0


def test_ruptura_que_toca_stop():
    cola = [
        {"close": 51, "high": 51.2, "low": 50.8, "volume": 1_000_000},
        {"close": 48, "high": 49, "low": 47.5, "volume": 1_000_000},  # toca stop (49.85) aquí
    ]
    df = _df_ruptura_con_cola(cola)
    operaciones = simular_operaciones(df, AJUSTES)

    assert len(operaciones) == 1
    op = operaciones[0]
    assert op["motivo_salida"] == "stop"
    assert op["precio_salida"] == 49.85
    assert op["dias_en_posicion"] == 2
    assert op["acierto"] is False
    assert op["beneficio_neto_euros"] < 0


def test_ruptura_sin_tocar_nada_cierra_por_tiempo():
    # 20 sesiones (el plazo de la regla de ruptura) sin tocar stop ni objetivo.
    cola = [{"close": 52.5 + i * 0.1, "high": 52.5 + i * 0.1 + 0.3, "low": 52.5 + i * 0.1 - 0.3, "volume": 1_000_000} for i in range(1, 21)]
    df = _df_ruptura_con_cola(cola)
    operaciones = simular_operaciones(df, AJUSTES)

    assert len(operaciones) == 1
    op = operaciones[0]
    assert op["motivo_salida"] == "tiempo"
    assert op["dias_en_posicion"] == 20
    assert op["precio_salida"] == pytest.approx(54.5, abs=0.01)

    # Seguimiento D+1/D+5/D+10/D+20 calculado sobre el cierre real de esos días.
    assert op["seguimiento_d1_pct"] == pytest.approx((52.6 / 52.5 - 1) * 100, abs=0.01)
    assert op["seguimiento_d5_pct"] == pytest.approx((53.0 / 52.5 - 1) * 100, abs=0.01)
    assert op["seguimiento_d10_pct"] == pytest.approx((53.5 / 52.5 - 1) * 100, abs=0.01)
    assert op["seguimiento_d20_pct"] == pytest.approx((54.5 / 52.5 - 1) * 100, abs=0.01)


def test_sin_senal_no_genera_operaciones():
    df = _con_fechas(
        pd.DataFrame({"close": [50.0] * 300, "high": [51.5] * 300, "low": [49.0] * 300, "volume": [1_000_000] * 300})
    )
    assert simular_operaciones(df, AJUSTES) == []


def test_resumen_fiabilidad_agrega_por_regla_y_seguimiento():
    operaciones = [
        {
            "regla": "Ruptura de máximos con volumen",
            "acierto": True,
            "retorno_pct": 10.0,
            "beneficio_riesgo_neto": 2.0,
            "seguimiento_d1_pct": 1.0,
            "seguimiento_d5_pct": 2.0,
            "seguimiento_d10_pct": 3.0,
            "seguimiento_d20_pct": 4.0,
        },
        {
            "regla": "Ruptura de máximos con volumen",
            "acierto": False,
            "retorno_pct": -5.0,
            "beneficio_riesgo_neto": -1.0,
            "seguimiento_d1_pct": -1.0,
            "seguimiento_d5_pct": None,
            "seguimiento_d10_pct": None,
            "seguimiento_d20_pct": None,
        },
    ]
    resumen = resumen_fiabilidad(operaciones)

    assert resumen["resumen_global"]["n_operaciones"] == 2
    assert resumen["resumen_global"]["tasa_acierto_pct"] == 50.0
    assert resumen["por_regla"]["Ruptura de máximos con volumen"]["n_operaciones"] == 2
    assert resumen["seguimiento_medio"]["d1_pct"] == 0.0  # media de 1.0 y -1.0
    assert resumen["seguimiento_medio"]["d5_pct"] == 2.0  # solo hay un dato (se ignoran los None)


def test_resumen_fiabilidad_sin_operaciones_no_rompe():
    resumen = resumen_fiabilidad([])
    assert resumen["resumen_global"]["n_operaciones"] == 0
    assert resumen["resumen_global"]["tasa_acierto_pct"] is None
    assert resumen["por_regla"] == {}


def test_comparacion_indice_calcula_retorno_total_y_anualizado():
    index_df = pd.DataFrame(
        {
            "date": [date(2020, 1, 1), date(2021, 1, 1), date(2022, 1, 1)],
            "close": [100.0, 150.0, 121.0],
        }
    )
    comparacion = comparacion_indice(index_df, date(2020, 1, 1), date(2022, 1, 1))

    assert comparacion is not None
    assert comparacion["retorno_total_pct"] == 21.0
    assert comparacion["retorno_anualizado_pct"] is not None


def test_comparacion_indice_sin_datos_en_el_periodo_devuelve_none():
    index_df = pd.DataFrame({"date": [date(2020, 1, 1)], "close": [100.0]})
    assert comparacion_indice(index_df, date(2021, 1, 1), date(2022, 1, 1)) is None
    assert comparacion_indice(pd.DataFrame(), date(2021, 1, 1), date(2022, 1, 1)) is None
