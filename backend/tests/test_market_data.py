import pytest

from app.services.market_data import MarketDataProvider, YFinanceProvider


def test_market_data_provider_es_abstracta():
    with pytest.raises(TypeError):
        MarketDataProvider()


def test_yfinance_provider_cumple_la_interfaz():
    assert isinstance(YFinanceProvider(), MarketDataProvider)
