from dataclasses import dataclass
from datetime import date, timedelta

from app.services.dividends import resumen_dividendos


@dataclass
class _Dividendo:
    date: date
    amount: float


def test_sin_dividendos_devuelve_todo_none():
    resumen = resumen_dividendos([], last_price=10.0)
    assert resumen["rentabilidad_pct"] is None
    assert resumen["fecha_estimada_proximo"] is None
    assert resumen["historial"] == []


def test_calcula_rentabilidad_sobre_el_ultimo_anio():
    hoy = date.today()
    dividendos = [
        _Dividendo(hoy - timedelta(days=30), 0.5),
        _Dividendo(hoy - timedelta(days=200), 0.5),
        _Dividendo(hoy - timedelta(days=500), 0.5),  # fuera del último año, no cuenta
    ]
    resumen = resumen_dividendos(dividendos, last_price=20.0)

    assert resumen["total_ultimo_anio_euros"] == 1.0
    assert resumen["rentabilidad_pct"] == 5.0  # 1.0 / 20.0 * 100
    assert resumen["fecha_ultimo"] == hoy - timedelta(days=30)
    assert resumen["importe_ultimo"] == 0.5


def test_sin_precio_no_calcula_rentabilidad_pero_si_lo_demas():
    dividendos = [_Dividendo(date.today(), 1.0)]
    resumen = resumen_dividendos(dividendos, last_price=None)
    assert resumen["rentabilidad_pct"] is None
    assert resumen["total_ultimo_anio_euros"] == 1.0


def test_fecha_estimada_proximo_usa_el_intervalo_medio():
    # Pagos cada 90 días -> el próximo se estima 90 días después del último.
    hoy = date.today()
    dividendos = [
        _Dividendo(hoy, 0.3),
        _Dividendo(hoy - timedelta(days=90), 0.3),
        _Dividendo(hoy - timedelta(days=180), 0.3),
    ]
    resumen = resumen_dividendos(dividendos, last_price=10.0)
    assert resumen["fecha_estimada_proximo"] == hoy + timedelta(days=90)


def test_un_solo_dividendo_no_puede_estimar_fecha():
    resumen = resumen_dividendos([_Dividendo(date.today(), 1.0)], last_price=10.0)
    assert resumen["fecha_estimada_proximo"] is None


def test_historial_limitado_a_ocho():
    hoy = date.today()
    dividendos = [_Dividendo(hoy - timedelta(days=30 * i), 0.1) for i in range(12)]
    resumen = resumen_dividendos(dividendos, last_price=10.0)
    assert len(resumen["historial"]) == 8
