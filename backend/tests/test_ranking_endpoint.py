from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.price import PriceBar

client = TestClient(app)


def _insertar_historico(db_session, ticker: str, precio_inicial: float, variacion_diaria_pct: float, n: int = 300):
    inicio = date(2024, 1, 1)
    barras = []
    precio = precio_inicial
    for i in range(n):
        barras.append(
            PriceBar(
                ticker=ticker,
                date=inicio + timedelta(days=i),
                open=precio,
                high=precio * 1.01,
                low=precio * 0.99,
                close=precio,
                volume=1_000_000,
            )
        )
        precio *= 1 + variacion_diaria_pct
    db_session.add_all(barras)
    db_session.commit()


def test_ranking_devuelve_las_35_empresas_del_ibex_y_ordena_por_score(db_session):
    _insertar_historico(db_session, "ACS.MC", 10, 0.004)
    _insertar_historico(db_session, "ACX.MC", 50, -0.002)

    r = client.get("/api/ranking?indice=IBEX35")
    assert r.status_code == 200
    ranking = r.json()
    assert len(ranking) == 35
    assert all(fila["indice"] == "IBEX35" for fila in ranking)

    por_ticker = {fila["ticker"]: fila for fila in ranking}
    assert por_ticker["ACS.MC"]["score_global"] is not None
    assert por_ticker["ACS.MC"]["score_global"] > por_ticker["ACX.MC"]["score_global"]

    # Una empresa sin histórico descargado no tiene factores calculables
    assert por_ticker["AENA.MC"]["momentum"] is None
    assert por_ticker["AENA.MC"]["score_global"] is None

    # Ordenado de mayor a menor score (los None al final)
    scores = [fila["score_global"] for fila in ranking if fila["score_global"] is not None]
    assert scores == sorted(scores, reverse=True)
