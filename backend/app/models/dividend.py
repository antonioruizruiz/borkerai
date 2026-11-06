from datetime import date

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Dividend(Base):
    """Un dividendo pagado por una empresa en una fecha concreta."""

    __tablename__ = "dividends"
    __table_args__ = (UniqueConstraint("ticker", "date", name="uq_dividend_ticker_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("companies.ticker"), index=True)
    date: Mapped[date]
    amount: Mapped[float]
