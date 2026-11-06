from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.models.dividend import Dividend
from app.models.price import PriceBar

client = TestClient(app)


def test_dividendos_devuelve_las_35_empresas_del_ibex(db_session):
    r = client.get("/api/dividendos?indice=IBEX35")
    assert r.status_code == 200
    datos = r.json()
    assert len(datos) == 35
    assert all(d["indice"] == "IBEX35" for d in datos)


def test_dividendos_calcula_rentabilidad_de_una_empresa(db_session):
    db_session.add(PriceBar(ticker="ENG.MC", date=date(2024, 1, 2), open=20, high=20, low=20, close=20, volume=1))
    db_session.add(Dividend(ticker="ENG.MC", date=date.today(), amount=1.0))
    db_session.commit()

    r = client.get("/api/dividendos")
    assert r.status_code == 200
    eng = next(d for d in r.json() if d["ticker"] == "ENG.MC")
    assert eng["rentabilidad_pct"] == 5.0
    assert len(eng["historial"]) >= 1
