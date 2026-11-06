from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.index_bar import IndexBar

client = TestClient(app)


def test_fiabilidad_devuelve_la_forma_esperada(db_session):
    r = client.get("/api/fiabilidad")
    assert r.status_code == 200
    datos = r.json()

    assert "resumen_global" in datos
    assert "por_regla" in datos
    assert "seguimiento_medio" in datos
    assert set(datos["seguimiento_medio"].keys()) == {"d1_pct", "d5_pct", "d10_pct", "d20_pct"}
    assert "operaciones" in datos
    assert isinstance(datos["operaciones"], list)

    for operacion in datos["operaciones"]:
        assert operacion["entrada"] > operacion["stop"]
        assert operacion["objetivo"] > operacion["entrada"]


def test_fiabilidad_sin_filtro_no_compara_con_ningun_indice(db_session):
    r = client.get("/api/fiabilidad")
    assert r.status_code == 200
    datos = r.json()
    assert datos["comparacion_indice"] is None
    assert datos["comparacion_indice_nota"] is not None


def test_fiabilidad_sueltas_sin_indice_de_referencia(db_session):
    r = client.get("/api/fiabilidad?indice=NINGUNO")
    assert r.status_code == 200
    datos = r.json()
    assert datos["comparacion_indice"] is None
    assert "sueltas" in datos["comparacion_indice_nota"].lower()


def test_fiabilidad_con_filtro_ibex_compara_contra_su_indice(db_session):
    inicio = date(2023, 1, 2)
    db_session.add_all(
        [
            IndexBar(indice="IBEX35", date=inicio, open=9000, high=9000, low=9000, close=9000, volume=1),
            IndexBar(
                indice="IBEX35",
                date=inicio + timedelta(days=200),
                open=9500,
                high=9500,
                low=9500,
                close=9500,
                volume=1,
            ),
        ]
    )
    db_session.commit()

    r = client.get("/api/fiabilidad?indice=IBEX35")
    assert r.status_code == 200
    datos = r.json()
    # Solo hay comparación si además hay operaciones simuladas en ese periodo; en
    # cualquier caso, con el filtro puesto no debe aparecer la nota de "sin filtro".
    assert datos["comparacion_indice_nota"] is None
