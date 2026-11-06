from fastapi.testclient import TestClient

from app.main import app
from app.models.company import Company

client = TestClient(app)


def test_indices_devuelve_los_cuatro_grupos_con_conteos(db_session):
    r = client.get("/api/indices")
    assert r.status_code == 200
    datos = r.json()

    claves = {d["indice"] for d in datos}
    assert claves == {"IBEX35", "DOWJONES", "NASDAQ100", None}

    total = sum(d["n_empresas"] for d in datos)
    assert total == db_session.query(Company).count()
