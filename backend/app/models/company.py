from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Company(Base):
    """Una empresa. Puede pertenecer a un índice (`"IBEX35"`, `"DOWJONES"`,
    `"NASDAQ100"`) o a ninguno (acción suelta, `indice=None`). `moneda` es la
    moneda original de cotización (sin convertir: "EUR", "USD", "CHF"...)."""

    __tablename__ = "companies"

    ticker: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    sector: Mapped[str]
    indice: Mapped[Optional[str]] = mapped_column(default=None)
    moneda: Mapped[str] = mapped_column(default="EUR")
