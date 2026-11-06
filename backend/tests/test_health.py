from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_companies_has_35_del_ibex():
    r = client.get("/api/companies?indice=IBEX35")
    assert r.status_code == 200
    assert len(r.json()) == 35


def test_companies_sin_filtro_devuelve_todo_el_universo():
    r = client.get("/api/companies")
    assert r.status_code == 200
    assert len(r.json()) > 35
