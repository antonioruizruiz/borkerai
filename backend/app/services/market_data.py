"""Interfaz para proveedores de datos de mercado (precio, volumen, dividendos).

Hoy usamos `yfinance` (gratuito) para el prototipo. Si en el futuro hace falta cambiar
a un proveedor de pago (EODHD, Twelve Data, FMP...), basta con escribir una nueva clase
que implemente `MarketDataProvider`; el resto de la app no cambia.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import TypedDict


class PriceRecord(TypedDict):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class DividendRecord(TypedDict):
    date: date
    amount: float


class MarketDataProvider(ABC):
    @abstractmethod
    def get_history(self, ticker: str, start: date, end: date | None = None) -> list[PriceRecord]:
        """Histórico diario OHLCV de `ticker` entre `start` y `end` (hoy si no se indica)."""

    @abstractmethod
    def get_dividends(self, ticker: str, start: date) -> list[DividendRecord]:
        """Dividendos pagados por `ticker` desde `start`."""


class YFinanceProvider(MarketDataProvider):
    def get_history(self, ticker: str, start: date, end: date | None = None) -> list[PriceRecord]:
        import yfinance as yf

        df = yf.Ticker(ticker).history(start=start, end=end, interval="1d", auto_adjust=False)
        return [
            {
                "date": idx.date(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }
            for idx, row in df.iterrows()
        ]

    def get_dividends(self, ticker: str, start: date) -> list[DividendRecord]:
        import yfinance as yf

        series = yf.Ticker(ticker).dividends
        return [
            {"date": idx.date(), "amount": float(amount)}
            for idx, amount in series.items()
            if idx.date() >= start
        ]
