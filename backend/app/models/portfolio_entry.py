from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PortfolioEntry(Base):
    """Una operación real que Antonio ha hecho (o simula haber hecho) y quiere seguir
    en la página Cartera: cuántas acciones, a qué precio, cuándo, y con qué intención
    (corto plazo, largo plazo o por sus dividendos)."""

    __tablename__ = "portfolio_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("companies.ticker"), index=True)
    fecha_compra: Mapped[date]
    precio_compra: Mapped[float]
    cantidad: Mapped[int]
    tipo: Mapped[str]  # "corto_plazo" | "largo_plazo" | "dividendos"
    notas: Mapped[str | None] = mapped_column(default=None)
