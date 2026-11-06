from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_settings_devuelve_los_cinco_campos(db_session):
    r = client.get("/api/settings")
    assert r.status_code == 200
    datos = r.json()
    assert set(datos.keys()) == {
        "capital_total",
        "riesgo_pct_operacion",
        "comision_pct",
        "comision_minima",
        "deslizamiento_pct",
    }


def test_put_settings_actualiza_valores(db_session):
    nuevo = {
        "capital_total": 5_000.0,
        "riesgo_pct_operacion": 2.0,
        "comision_pct": 0.2,
        "comision_minima": 3.0,
        "deslizamiento_pct": 0.1,
    }
    r = client.put("/api/settings", json=nuevo)
    assert r.status_code == 200
    assert r.json() == nuevo

    r2 = client.get("/api/settings")
    assert r2.json() == nuevo
