from datetime import date

from app.services.portfolio import calcular_posicion, evaluar_aviso


def test_calcular_posicion_sin_precio_actual_devuelve_none():
    resultado = calcular_posicion(precio_compra=10.0, cantidad=5, precio_actual=None)
    assert resultado == {
        "precio_actual": None,
        "valor_actual_euros": None,
        "ganancia_perdida_euros": None,
        "ganancia_perdida_pct": None,
    }


def test_calcular_posicion_con_ganancia():
    resultado = calcular_posicion(precio_compra=10.0, cantidad=10, precio_actual=12.0)
    assert resultado["valor_actual_euros"] == 120.0
    assert resultado["ganancia_perdida_euros"] == 20.0
    assert resultado["ganancia_perdida_pct"] == 20.0


def test_calcular_posicion_con_perdida():
    resultado = calcular_posicion(precio_compra=10.0, cantidad=10, precio_actual=8.0)
    assert resultado["ganancia_perdida_euros"] == -20.0
    assert resultado["ganancia_perdida_pct"] == -20.0


def test_aviso_corto_plazo_con_perdida_grande():
    aviso = evaluar_aviso("corto_plazo", ganancia_perdida_pct=-6.0)
    assert aviso is not None and "Revisar" in aviso


def test_aviso_corto_plazo_con_ganancia_grande():
    aviso = evaluar_aviso("corto_plazo", ganancia_perdida_pct=16.0)
    assert aviso is not None and "beneficios" in aviso


def test_aviso_corto_plazo_sin_nada_relevante():
    assert evaluar_aviso("corto_plazo", ganancia_perdida_pct=2.0) is None


def test_aviso_largo_plazo_con_perdida_grande():
    aviso = evaluar_aviso("largo_plazo", ganancia_perdida_pct=-25.0)
    assert aviso is not None and "largo plazo" in aviso


def test_aviso_largo_plazo_con_perdida_pequena_no_avisa():
    assert evaluar_aviso("largo_plazo", ganancia_perdida_pct=-5.0) is None


def test_aviso_dividendos_con_fecha_estimada():
    proxima = date(2027, 1, 15)
    aviso = evaluar_aviso("dividendos", ganancia_perdida_pct=1.0, fecha_estimada_proximo_dividendo=proxima)
    assert aviso == "Próximo dividendo estimado el 15/01/2027."


def test_aviso_dividendos_sin_fecha_estimada():
    assert evaluar_aviso("dividendos", ganancia_perdida_pct=1.0, fecha_estimada_proximo_dividendo=None) is None
