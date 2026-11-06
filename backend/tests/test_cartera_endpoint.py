from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.models.price import PriceBar

client = TestClient(app)


def test_crear_posicion_empresa_desconocida_404(db_session):
    r = client.post(
        "/api/cartera",
        json={
            "ticker": "NOEXISTE.MC",
            "fecha_compra": "2024-01-01",
            "precio_compra": 10.0,
            "cantidad": 5,
            "tipo": "largo_plazo",
        },
    )
    assert r.status_code == 404


def test_crear_y_listar_posicion_sin_precio_devuelve_campos_none(db_session):
    r = client.post(
        "/api/cartera",
        json={
            "ticker": "MAP.MC",
            "fecha_compra": "2024-01-01",
            "precio_compra": 2.0,
            "cantidad": 100,
            "tipo": "largo_plazo",
        },
    )
    assert r.status_code == 200
    creada = r.json()
    assert creada["precio_actual"] is None
    assert creada["ganancia_perdida_euros"] is None

    r2 = client.get("/api/cartera")
    assert r2.status_code == 200
    datos = r2.json()
    assert any(p["ticker"] == "MAP.MC" for p in datos["posiciones"])


def test_posicion_corto_plazo_con_perdida_genera_aviso(db_session):
    db_session.add_all(
        [
            PriceBar(ticker="FER.MC", date=date(2024, 1, 2), open=100, high=100, low=100, close=100, volume=1),
            PriceBar(ticker="FER.MC", date=date(2024, 1, 3), open=90, high=90, low=90, close=90, volume=1),
        ]
    )
    db_session.commit()

    r = client.post(
        "/api/cartera",
        json={
            "ticker": "FER.MC",
            "fecha_compra": "2024-01-02",
            "precio_compra": 100.0,
            "cantidad": 10,
            "tipo": "corto_plazo",
        },
    )
    assert r.status_code == 200
    creada = r.json()
    assert creada["ganancia_perdida_pct"] == -10.0
    assert creada["aviso"] is not None
    assert "Revisar" in creada["aviso"]


def test_resumen_cartera_suma_las_posiciones(db_session):
    r = client.get("/api/cartera")
    assert r.status_code == 200
    resumen = r.json()["resumen"]
    assert resumen["valor_invertido_euros"] > 0


def test_borrar_posicion(db_session):
    r = client.post(
        "/api/cartera",
        json={
            "ticker": "ITX.MC",
            "fecha_compra": "2024-01-01",
            "precio_compra": 30.0,
            "cantidad": 1,
            "tipo": "dividendos",
        },
    )
    entrada_id = r.json()["id"]

    r_borrar = client.delete(f"/api/cartera/{entrada_id}")
    assert r_borrar.status_code == 204

    r_borrar_otra_vez = client.delete(f"/api/cartera/{entrada_id}")
    assert r_borrar_otra_vez.status_code == 404
