"""Alta y baja de "acciones sueltas" (empresas sin índice) añadidas a mano desde
la página "Añadir acción" del frontend, sin pasar por los ficheros de `app/data/`."""
from datetime import date

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.dividend import Dividend
from app.models.price import PriceBar
from app.services.market_data import MarketDataProvider, YFinanceProvider

YEARS_HISTORIAL_INICIAL = 10


class TickerSinDatosError(Exception):
    """El ticker no ha devuelto ningún precio en Yahoo Finance (probablemente mal escrito)."""


def agregar_empresa_suelta(
    db: Session,
    ticker: str,
    name: str,
    sector: str,
    moneda: str,
    provider: MarketDataProvider | None = None,
) -> Company:
    """Crea la empresa (indice=None) y descarga de inmediato su histórico de los
    últimos `YEARS_HISTORIAL_INICIAL` años, para que no aparezca vacía en la app
    hasta el próximo `download_history.py`. Lanza `TickerSinDatosError` si Yahoo
    Finance no devuelve ningún precio (ticker probablemente incorrecto), sin dejar
    la empresa creada a medias.
    """
    provider = provider or YFinanceProvider()
    hoy = date.today()
    inicio = date(hoy.year - YEARS_HISTORIAL_INICIAL, hoy.month, hoy.day)

    try:
        precios = provider.get_history(ticker, start=inicio)
    except Exception as exc:
        raise TickerSinDatosError(f"No se ha podido consultar Yahoo Finance para «{ticker}»: {exc}") from exc

    if not precios:
        raise TickerSinDatosError(
            f"Yahoo Finance no tiene precios para «{ticker}». Revisa que el ticker sea correcto, "
            "incluyendo el sufijo de la bolsa (p. ej. .PA para París, .DE para Fráncfort, .SW para Zúrich)."
        )

    try:
        dividendos = provider.get_dividends(ticker, start=inicio)
    except Exception:
        dividendos = []

    company = Company(ticker=ticker, name=name, sector=sector, moneda=moneda, indice=None)
    db.add(company)
    db.add_all(PriceBar(ticker=ticker, **r) for r in precios)
    db.add_all(Dividend(ticker=ticker, **r) for r in dividendos)
    db.commit()
    db.refresh(company)
    return company


def borrar_empresa_suelta(db: Session, company: Company) -> None:
    """Borra la empresa y todo su histórico (precios y dividendos). Solo para
    acciones sueltas: las de un índice se gestionan por los ficheros de `app/data/`."""
    db.query(PriceBar).filter(PriceBar.ticker == company.ticker).delete()
    db.query(Dividend).filter(Dividend.ticker == company.ticker).delete()
    db.delete(company)
    db.commit()
