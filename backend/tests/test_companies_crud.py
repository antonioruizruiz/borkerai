"""Alta y baja de acciones sueltas desde la página "Añadir acción" (POST/DELETE
/api/companies). Se sustituye YFinanceProvider por un doble de prueba para no
depender de la red ni de datos reales de mercado."""
from datetime import date

from fastapi.testclient import TestClient

import app.services.company_management as company_management
from app.main import app

client = TestClient(app)


class _ProviderConDatos:
    def get_history(self, ticker, start, end=None):
        return [
            {"date": date(2024, 1, 2), "open": 10.0, "high": 10.5, "low": 9.5, "close": 10.2, "volume": 1_000},
            {"date": date(2024, 1, 3), "open": 10.2, "high": 10.8, "low": 10.0, "close": 10.6, "volume": 1_200},
        ]

    def get_dividends(self, ticker, start):
        return []


class _ProviderSinDatos:
    def get_history(self, ticker, start, end=None):
        return []

    def get_dividends(self, ticker, start):
        return []


def test_crear_y_borrar_empresa_suelta(db_session, monkeypatch):
    monkeypatch.setattr(company_management, "YFinanceProvider", _ProviderConDatos)

    r = client.post(
        "/api/companies",
        json={"ticker": "test.pa", "name": "Empresa de prueba", "sector": "Lujo", "moneda": "eur"},
    )
    assert r.status_code == 201
    creada = r.json()
    assert creada["ticker"] == "TEST.PA"
    assert creada["indice"] is None
    assert creada["moneda"] == "EUR"
    assert creada["last_price"] == 10.6

    r_listado = client.get("/api/companies?indice=NINGUNO")
    assert any(c["ticker"] == "TEST.PA" for c in r_listado.json())

    r_borrar = client.delete("/api/companies/TEST.PA")
    assert r_borrar.status_code == 204

    r_listado_tras_borrar = client.get("/api/companies?indice=NINGUNO")
    assert not any(c["ticker"] == "TEST.PA" for c in r_listado_tras_borrar.json())


def test_crear_empresa_duplicada_409(db_session):
    r = client.post(
        "/api/companies",
        json={"ticker": "ACS.MC", "name": "ACS", "sector": "Construcción", "moneda": "EUR"},
    )
    assert r.status_code == 409


def test_crear_empresa_sin_datos_en_yahoo_400(db_session, monkeypatch):
    monkeypatch.setattr(company_management, "YFinanceProvider", _ProviderSinDatos)

    r = client.post(
        "/api/companies",
        json={"ticker": "NOEXISTE123", "name": "No existe", "sector": "Desconocido", "moneda": "USD"},
    )
    assert r.status_code == 400


def test_borrar_empresa_de_un_indice_no_permitido(db_session):
    r = client.delete("/api/companies/ACS.MC")
    assert r.status_code == 400


def test_borrar_empresa_inexistente_404(db_session):
    r = client.delete("/api/companies/NOEXISTE.XX")
    assert r.status_code == 404
