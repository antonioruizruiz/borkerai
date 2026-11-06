from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import TradingSettingsIn, TradingSettingsOut
from app.core.db import get_db
from app.models.trading_settings import TradingSettings

router = APIRouter(prefix="/api", tags=["settings"])


def get_or_create_settings(db: Session) -> TradingSettings:
    ajustes = db.query(TradingSettings).filter(TradingSettings.id == 1).first()
    if ajustes is None:
        ajustes = TradingSettings(id=1)
        db.add(ajustes)
        db.commit()
        db.refresh(ajustes)
    return ajustes


@router.get("/settings", response_model=TradingSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    """Capital, riesgo por operación y costes usados para generar los planes de la página Hoy."""
    return get_or_create_settings(db)


@router.put("/settings", response_model=TradingSettingsOut)
def update_settings(datos: TradingSettingsIn, db: Session = Depends(get_db)):
    ajustes = get_or_create_settings(db)
    for campo, valor in datos.model_dump().items():
        setattr(ajustes, campo, valor)
    db.commit()
    db.refresh(ajustes)
    return ajustes
