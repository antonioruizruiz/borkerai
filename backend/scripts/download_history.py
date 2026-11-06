"""Descarga 10 años de histórico diario y dividendos de todo el universo de empresas
(IBEX 35 + Dow Jones + Nasdaq-100 + acciones sueltas, incluidas las añadidas a mano
desde la página "Añadir acción") y de los 3 índices de referencia, guardándolo en la
base de datos. Es un proceso que solo hace falta lanzar de vez en cuando (no en cada
arranque del servidor); tarda varios minutos.

Uso (desde backend/, con el entorno virtual activado):
    python scripts/download_history.py
"""
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import SessionLocal, init_db  # noqa: E402
from app.models.company import Company  # noqa: E402
from app.models.dividend import Dividend  # noqa: E402
from app.models.index_bar import IndexBar  # noqa: E402
from app.models.price import PriceBar  # noqa: E402
from app.services.market_data import YFinanceProvider  # noqa: E402

YEARS_HISTORY = 10
PAUSA_ENTRE_VALORES_SEGUNDOS = 1  # para no saturar a Yahoo Finance

# Ticker de Yahoo Finance del propio índice, por cada índice que seguimos (Fase 5: comparar el backtest).
TICKERS_INDICES = {"IBEX35": "^IBEX", "DOWJONES": "^DJI", "NASDAQ100": "^NDX"}


def upsert_prices(db, ticker: str, records: list[dict]) -> int:
    existentes = {d for (d,) in db.query(PriceBar.date).filter(PriceBar.ticker == ticker).all()}
    nuevos = [PriceBar(ticker=ticker, **r) for r in records if r["date"] not in existentes]
    db.add_all(nuevos)
    return len(nuevos)


def upsert_dividends(db, ticker: str, records: list[dict]) -> int:
    existentes = {d for (d,) in db.query(Dividend.date).filter(Dividend.ticker == ticker).all()}
    nuevos = [Dividend(ticker=ticker, **r) for r in records if r["date"] not in existentes]
    db.add_all(nuevos)
    return len(nuevos)


def upsert_index(db, indice: str, records: list[dict]) -> int:
    existentes = {d for (d,) in db.query(IndexBar.date).filter(IndexBar.indice == indice).all()}
    nuevos = [IndexBar(indice=indice, **r) for r in records if r["date"] not in existentes]
    db.add_all(nuevos)
    return len(nuevos)


def main() -> None:
    init_db()
    provider = YFinanceProvider()
    hoy = date.today()
    inicio = date(hoy.year - YEARS_HISTORY, hoy.month, hoy.day)

    db = SessionLocal()
    try:
        for indice, ticker_indice in TICKERS_INDICES.items():
            print(f"[índice] {indice} ({ticker_indice})...", end=" ", flush=True)
            try:
                velas_indice = provider.get_history(ticker_indice, start=inicio)
                n_indice = upsert_index(db, indice, velas_indice)
                db.commit()
                print(f"{n_indice} velas nuevas")
            except Exception as exc:
                print(f"ERROR: {exc}")

        # El universo semilla (IBEX35 + DowJones + Nasdaq100 + sueltas de `app/data/`)
        # se siembra en init_db(); aquí partimos de la BD para incluir también las
        # acciones sueltas añadidas a mano desde la página "Añadir acción".
        empresas = db.query(Company).order_by(Company.ticker).all()
        for i, company in enumerate(empresas, start=1):
            ticker = company.ticker
            print(f"[{i}/{len(empresas)}] {ticker} ({company.name})...", end=" ", flush=True)

            try:
                precios = provider.get_history(ticker, start=inicio)
                dividendos = provider.get_dividends(ticker, start=inicio)
            except Exception as exc:
                # Un fallo puntual (p. ej. ticker sin datos) no debe parar todo el proceso.
                print(f"ERROR: {exc}")
                continue

            n_precios = upsert_prices(db, ticker, precios)
            n_dividendos = upsert_dividends(db, ticker, dividendos)
            db.commit()
            print(f"{n_precios} velas nuevas, {n_dividendos} dividendos nuevos")

            time.sleep(PAUSA_ENTRE_VALORES_SEGUNDOS)
    finally:
        db.close()

    print("Descarga completada.")


if __name__ == "__main__":
    main()
