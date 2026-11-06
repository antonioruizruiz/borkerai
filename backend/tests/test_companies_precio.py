from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.models.price import PriceBar

client = TestClient(app)


def test_companies_sin_precios_devuelve_null(db_session):
    r = client.get("/api/companies")
    assert r.status_code == 200
    acs = next(c for c in r.json() if c["ticker"] == "ACS.MC")
    assert acs["last_price"] is None
    assert acs["change_pct"] is None


def test_companies_filtra_por_indice(db_session):
    r = client.get("/api/companies?indice=DOWJONES")
    assert r.status_code == 200
    datos = r.json()
    assert all(c["indice"] == "DOWJONES" for c in datos)
    # AAPL/MSFT/NVDA/AMZN/CSCO/HON/AMGN están también en el Dow pero se resuelven a Nasdaq-100
    assert not any(c["ticker"] == "AAPL" for c in datos)
    assert any(c["ticker"] == "BA" for c in datos)


def test_companies_filtra_sueltas(db_session):
    r = client.get("/api/companies?indice=NINGUNO")
    assert r.status_code == 200
    datos = r.json()
    assert all(c["indice"] is None for c in datos)
    assert any(c["ticker"] == "MC.PA" for c in datos)
    assert not any(c["ticker"].endswith(".MC") for c in datos)


def test_companies_calcula_variacion(db_session):
    db_session.add_all(
        [
            PriceBar(ticker="ANA.MC", date=date(2024, 1, 2), open=100, high=100, low=100, close=100, volume=1),
            PriceBar(ticker="ANA.MC", date=date(2024, 1, 3), open=100, high=100, low=100, close=110, volume=1),
        ]
    )
    db_session.commit()

    r = client.get("/api/companies")
    assert r.status_code == 200
    ana = next(c for c in r.json() if c["ticker"] == "ANA.MC")
    assert ana["last_price"] == 110
    assert round(ana["change_pct"], 2) == 10.0
    assert ana["last_price_date"] == "2024-01-03"
