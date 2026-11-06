from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.schemas import IndiceOut
from app.core.db import get_db
from app.models.company import Company

router = APIRouter(prefix="/api", tags=["indices"])

NOMBRES = {"IBEX35": "IBEX 35", "DOWJONES": "Dow Jones", "NASDAQ100": "Nasdaq-100"}


@router.get("/indices", response_model=list[IndiceOut])
def list_indices(db: Session = Depends(get_db)):
    """Índices disponibles (más "sueltas", indice=None) con el nº de empresas en cada
    uno, para poblar el selector de índice del frontend."""
    filas = db.query(Company.indice, func.count(Company.ticker)).group_by(Company.indice).all()
    resultado = [
        {"indice": indice, "nombre": NOMBRES.get(indice, "Sin índice (sueltas)"), "n_empresas": n}
        for indice, n in filas
    ]
    resultado.sort(key=lambda r: (r["indice"] is None, r["indice"]))
    return resultado
