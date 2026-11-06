from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_recomendaciones_devuelve_las_dos_listas(db_session):
    r = client.get("/api/recomendaciones")
    assert r.status_code == 200
    datos = r.json()
    assert "recomendaciones" in datos
    assert "vigilancia" in datos
    assert isinstance(datos["recomendaciones"], list)
    assert isinstance(datos["vigilancia"], list)
    for fila in datos["recomendaciones"]:
        assert fila["entrada"] > fila["stop"]
        assert fila["objetivo"] > fila["entrada"]
        assert fila["acciones"] >= 0
