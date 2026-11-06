from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TradingSettings(Base):
    """Parámetros de capital, riesgo y costes que edita el usuario en Ajustes.

    Fila única (id=1): no hay varios usuarios todavía (ver Fase 8).
    """

    __tablename__ = "trading_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    capital_total: Mapped[float] = mapped_column(default=10_000.0)
    riesgo_pct_operacion: Mapped[float] = mapped_column(default=1.0)
    comision_pct: Mapped[float] = mapped_column(default=0.1)
    comision_minima: Mapped[float] = mapped_column(default=2.0)
    deslizamiento_pct: Mapped[float] = mapped_column(default=0.05)
