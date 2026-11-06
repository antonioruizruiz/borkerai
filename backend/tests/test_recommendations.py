from types import SimpleNamespace

import pandas as pd

from app.services.recommendations import generar_recomendacion

AJUSTES = SimpleNamespace(
    capital_total=10_000.0,
    riesgo_pct_operacion=1.0,
    comision_pct=0.1,
    comision_minima=2.0,
    deslizamiento_pct=0.05,
)


def _df_ruptura(jump_pct: float, vol_multiplier: float, n_base: int = 279) -> pd.DataFrame:
    """n_base sesiones planas a 50 € y una última sesión con un salto de precio y volumen."""
    precios = [50.0] * n_base
    precios.append(precios[-1] * (1 + jump_pct))
    volumes = [1_000_000] * n_base + [int(1_000_000 * vol_multiplier)]
    return pd.DataFrame(
        {
            "close": precios,
            "high": [p * 1.003 for p in precios[:-1]] + [precios[-1] * 1.001],
            "low": [p * 0.997 for p in precios],
            "volume": volumes,
        }
    )


def _df_pullback(n_rebote: int, tasa_rebote: float) -> pd.DataFrame:
    """Sube en tendencia, cae, se estabiliza y rebota ligeramente (retroceso clásico)."""
    precios = [10 * (1.0035**i) for i in range(230)]
    ultimo = precios[-1]
    for _ in range(10):
        ultimo *= 1 - 0.004
        precios.append(ultimo)
    for _ in range(33):
        precios.append(ultimo)
    for _ in range(n_rebote):
        ultimo *= 1 + tasa_rebote
        precios.append(ultimo)
    return pd.DataFrame(
        {
            "close": precios,
            "high": [p * 1.003 for p in precios],
            "low": [p * 0.997 for p in precios],
            "volume": [1_000_000] * len(precios),
        }
    )


def test_sin_historico_suficiente_no_hay_recomendacion():
    df = _df_ruptura(0.05, 3.0, n_base=100)
    assert generar_recomendacion(df, estabilidad=80, ajustes=AJUSTES) is None


def test_ruptura_con_volumen_genera_plan_completo():
    df = _df_ruptura(jump_pct=0.05, vol_multiplier=3.0)
    resultado = generar_recomendacion(df, estabilidad=80, ajustes=AJUSTES)

    assert resultado is not None
    assert resultado["regla"] == "Ruptura de máximos con volumen"
    assert "vigilancia" not in resultado
    assert resultado["entrada"] > resultado["stop"]
    assert resultado["objetivo"] > resultado["entrada"]
    assert resultado["acciones"] > 0
    assert resultado["beneficio_riesgo_neto"] > 0
    assert resultado["riesgo"] == "bajo"  # estabilidad=80 -> bajo riesgo
    assert resultado["plazo"] == "corto plazo (2-4 semanas)"


def test_cerca_de_romper_maximos_sin_volumen_queda_en_vigilancia():
    df = _df_ruptura(jump_pct=-0.005, vol_multiplier=1.0)
    resultado = generar_recomendacion(df, estabilidad=80, ajustes=AJUSTES)

    assert resultado is not None
    assert resultado.get("vigilancia") is True
    assert resultado["regla"] == "Cerca de romper máximos"
    assert "entrada" not in resultado


def test_retroceso_en_tendencia_alcista_genera_plan_completo():
    df = _df_pullback(n_rebote=3, tasa_rebote=0.005)
    resultado = generar_recomendacion(df, estabilidad=50, ajustes=AJUSTES)

    assert resultado is not None
    assert resultado["regla"] == "Retroceso en tendencia alcista"
    assert resultado["entrada"] > resultado["stop"]
    assert resultado["acciones"] > 0
    assert resultado["riesgo"] == "medio"  # estabilidad=50 -> medio riesgo
    assert resultado["plazo"] == "medio plazo (1-3 meses)"


def test_posible_retroceso_queda_en_vigilancia():
    df = _df_pullback(n_rebote=0, tasa_rebote=0.0)
    resultado = generar_recomendacion(df, estabilidad=50, ajustes=AJUSTES)

    assert resultado is not None
    assert resultado.get("vigilancia") is True
    assert resultado["regla"] == "Posible retroceso en tendencia alcista"


def test_sin_senal_no_hay_recomendacion():
    # Serie completamente plana y bien alejada de su máximo (ni ruptura ni tendencia ni volumen fuera de lo normal).
    df = pd.DataFrame(
        {
            "close": [50.0] * 280,
            "high": [51.5] * 280,
            "low": [49.0] * 280,
            "volume": [1_000_000] * 280,
        }
    )
    assert generar_recomendacion(df, estabilidad=50, ajustes=AJUSTES) is None


def test_riesgo_demasiado_bajo_para_una_sola_accion_no_da_plan():
    df = _df_ruptura(jump_pct=0.05, vol_multiplier=3.0)
    ajustes_capital_minimo = SimpleNamespace(**{**AJUSTES.__dict__, "capital_total": 1.0})
    assert generar_recomendacion(df, estabilidad=80, ajustes=ajustes_capital_minimo) is None
