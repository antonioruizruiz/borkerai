from app.data.universo import universo_completo


def test_universo_no_tiene_tickers_duplicados():
    datos = universo_completo()
    tickers = [c["ticker"] for c in datos]
    assert len(tickers) == len(set(tickers))


def test_solapes_dow_nasdaq_se_resuelven_a_nasdaq100():
    datos = {c["ticker"]: c for c in universo_completo()}
    for ticker in ("AAPL", "MSFT", "NVDA", "AMZN", "CSCO", "HON", "AMGN"):
        assert datos[ticker]["indice"] == "NASDAQ100"


def test_sueltas_sin_indice():
    datos = {c["ticker"]: c for c in universo_completo()}
    assert datos["MC.PA"]["indice"] is None
    assert datos["MC.PA"]["moneda"] == "EUR"


def test_ibex35_tiene_35_empresas_en_eur():
    datos = [c for c in universo_completo() if c["indice"] == "IBEX35"]
    assert len(datos) == 35
    assert all(c["moneda"] == "EUR" for c in datos)
