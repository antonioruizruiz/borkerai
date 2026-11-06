from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.filters import filtrar_por_indice
from app.api.ranking import cargar_precios
from app.api.schemas import FiabilidadOut
from app.api.settings import get_or_create_settings
from app.core.db import get_db
from app.models.company import Company
from app.models.index_bar import IndexBar
from app.services.backtest import comparacion_indice, resumen_fiabilidad, simular_operaciones

router = APIRouter(prefix="/api", tags=["fiabilidad"])

NOTA_SIN_FILTRO = "Selecciona un índice para comparar con su referencia (al mezclar varios índices no hay un único benchmark)."
NOTA_SUELTAS = "Las acciones sueltas no tienen índice de referencia."


def _cargar_indice(db: Session, indice: str) -> pd.DataFrame:
    velas = db.query(IndexBar).filter(IndexBar.indice == indice).order_by(IndexBar.date).all()
    return pd.DataFrame([{"date": v.date, "close": v.close} for v in velas])


@router.get("/fiabilidad", response_model=FiabilidadOut)
def get_fiabilidad(indice: str | None = None, db: Session = Depends(get_db)):
    """Backtest de las reglas de entrada (Fase 4) sobre los 10 años de histórico ya
    descargados: qué habría pasado con cada señal pasada, con costes descontados, y
    (si se filtra por un único índice) cómo se compara con haberse quedado quieto en
    ese índice durante el mismo periodo.

    LIMITACIÓN CONOCIDA: `ajustes.capital_total` está en EUR; para empresas en otra
    moneda, el tamaño de posición y los importes "_euros" se calculan como si el
    precio ya estuviera en EUR (no hay conversión de divisa todavía). El `%` de
    retorno sí es correcto en cualquier moneda.
    """
    ajustes = get_or_create_settings(db)
    companies = filtrar_por_indice(db.query(Company), indice).order_by(Company.ticker).all()

    operaciones: list[dict] = []
    for company in companies:
        df = cargar_precios(db, company.ticker)
        for operacion in simular_operaciones(df, ajustes):
            operaciones.append(
                {"ticker": company.ticker, "name": company.name, "moneda": company.moneda, **operacion}
            )

    operaciones.sort(key=lambda o: o["fecha_entrada"])

    resumen = resumen_fiabilidad(operaciones)

    comparacion = None
    nota_comparacion = None
    if indice is None:
        nota_comparacion = NOTA_SIN_FILTRO
    elif indice.upper() == "NINGUNO":
        nota_comparacion = NOTA_SUELTAS
    elif operaciones:
        periodo_inicio: date = operaciones[0]["fecha_entrada"]
        periodo_fin: date = max(o["fecha_salida"] for o in operaciones)
        comparacion = comparacion_indice(_cargar_indice(db, indice.upper()), periodo_inicio, periodo_fin)

    return {
        **resumen,
        "comparacion_indice": comparacion,
        "comparacion_indice_nota": nota_comparacion,
        "operaciones": operaciones,
    }
